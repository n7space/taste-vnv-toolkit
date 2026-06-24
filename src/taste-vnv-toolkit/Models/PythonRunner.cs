using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Python.Runtime;

namespace taste_vnv_toolkit.Models;

/// <summary>Parameters for a single status-script invocation.</summary>
public record StatusScriptRequest(
    string ScriptPath,
    string ToolDirectory,
    string? ProjectDirectory,
    string? IntermediateDirectory,
    string? OutputDirectory,
    IEnumerable<(string Name, object Value)> Settings);

/// <summary>
/// Runs Python scripts via pythonnet.
/// <para>
/// All Python calls are serialised through a single long-lived worker thread.
/// This guarantees that the Python GIL is always acquired and released on the
/// same OS thread, avoiding the thread-state mismatch that crashes the process
/// when <c>BeginAllowThreads</c>/<c>EndAllowThreads</c> are used naively.
/// </para>
/// <para>
/// Call <see cref="Initialize"/> exactly once at startup and
/// <see cref="Shutdown"/> exactly once at exit.
/// </para>
/// </summary>
public static class PythonRunner
{
    private static volatile bool _initialized = false;

    // Every Python call is posted here; the single worker thread consumes them.
    private static readonly BlockingCollection<Action> _workQueue =
        new(new ConcurrentQueue<Action>());

    static PythonRunner()
    {
        var worker = new Thread(() =>
        {
            foreach (var action in _workQueue.GetConsumingEnumerable())
                action();
        })
        {
            IsBackground = true,
            Name = "PythonWorker"
        };
        worker.Start();
    }

    // ── Lifecycle (call once per process) ─────────────────────────────────────

    /// <summary>
    /// Initialises the Python engine on the Python worker thread.
    /// Call once at application startup before any script methods.
    /// </summary>
    public static void Initialize()
    {
        if (_initialized) return;
        DispatchSync(() =>
        {
            try
            {
                EnsurePythonDllConfigured();
                PythonEngine.Initialize();
                _initialized = true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Python initialisation failed: {ex.Message}");
            }
        });
    }

    /// <summary>
    /// Shuts down the Python engine on the Python worker thread.
    /// Call once at application exit.
    /// </summary>
    public static void Shutdown()
    {
        if (!_initialized) return;
        DispatchSync(() =>
        {
            _initialized = false;
            try { PythonEngine.Shutdown(); } catch { }
        });
    }

    // ── Public API ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Runs every status script in <paramref name="requests"/> sequentially on
    /// the Python worker thread.  Results are returned in the same order as the
    /// requests.
    /// </summary>
    public static Task<IReadOnlyList<StatusScriptResult>> RunStatusBatchAsync(
        IEnumerable<StatusScriptRequest> requests)
    {
        var list = requests.ToList();
        if (!_initialized)
            return Task.FromResult<IReadOnlyList<StatusScriptResult>>(
                list.Select(_ => new StatusScriptResult(ToolStatus.Error, "Python runtime not available"))
                    .ToList());

        return DispatchAsync<IReadOnlyList<StatusScriptResult>>(
            () => list.Select(RunStatusScriptCore).ToList());
    }

    /// <summary>Runs a single view script on the Python worker thread.</summary>
    public static Task<ToolScriptResult> RunViewScriptAsync(
        string scriptPath,
        string toolDirectory,
        string? projectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings)
    {
        if (!_initialized)
            return Task.FromResult(
                new ToolScriptResult(ToolStatus.Error, "Python runtime not available", true));

        return DispatchAsync(() =>
            RunToolOrViewScriptCore(scriptPath, toolDirectory, projectDirectory,
                intermediateDirectory, outputDirectory, settings, null));
    }

    /// <summary>Runs a single tool script on the Python worker thread.</summary>
    public static Task<ToolScriptResult> RunToolScriptAsync(
        string scriptPath,
        string toolDirectory,
        string? projectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings,
        Action<int>? reportProgress)
    {
        if (!_initialized)
            return Task.FromResult(
                new ToolScriptResult(ToolStatus.Error, "Python runtime not available", true));

        return DispatchAsync(() =>
            RunToolOrViewScriptCore(scriptPath, toolDirectory, projectDirectory,
                intermediateDirectory, outputDirectory, settings, reportProgress));
    }

    // ── Worker-thread dispatch ────────────────────────────────────────────────

    /// <summary>Posts <paramref name="action"/> to the Python worker thread and
    /// blocks the caller until it completes.</summary>
    private static void DispatchSync(Action action)
        => DispatchAsync(() => { action(); return 0; }).GetAwaiter().GetResult();

    /// <summary>Posts <paramref name="body"/> to the Python worker thread and
    /// returns a Task that completes with the result.</summary>
    private static Task<T> DispatchAsync<T>(Func<T> body)
    {
        var tcs = new TaskCompletionSource<T>(
            TaskCreationOptions.RunContinuationsAsynchronously);
        _workQueue.Add(() =>
        {
            try { tcs.SetResult(body()); }
            catch (Exception ex) { tcs.SetException(ex); }
        });
        return tcs.Task;
    }

    // ── Python DLL discovery ──────────────────────────────────────────────────

    private static void EnsurePythonDllConfigured()
    {
        if (!string.IsNullOrEmpty(Runtime.PythonDLL))
            return;

        try
        {
            var psi = new ProcessStartInfo("python3")
            {
                Arguments = "-c \"import sysconfig, os; "
                          + "d = sysconfig.get_config_var('LIBDIR'); "
                          + "l = sysconfig.get_config_var('LDLIBRARY'); "
                          + "print(os.path.join(d, l))\"",
                RedirectStandardOutput = true,
                UseShellExecute = false,
            };
            using var proc = Process.Start(psi);
            if (proc is not null)
            {
                var path = proc.StandardOutput.ReadToEnd().Trim();
                proc.WaitForExit();
                if (!string.IsNullOrEmpty(path) && File.Exists(path))
                    Runtime.PythonDLL = path;
            }
        }
        catch { /* let PythonEngine.Initialize() use its own discovery */ }
    }

    // ── Script execution (always called on the Python worker thread) ──────────

    private static StatusScriptResult RunStatusScriptCore(StatusScriptRequest req)
    {
        if (!File.Exists(req.ScriptPath))
            return new StatusScriptResult(ToolStatus.Error, $"Script not found: {req.ScriptPath}");

        try
        {
            using (Py.GIL())
            {
                using var scope = Py.CreateScope();
                SetCommonVariables(scope, req.ToolDirectory, req.ProjectDirectory,
                    req.IntermediateDirectory, req.OutputDirectory, req.Settings, null);
                scope.Exec(File.ReadAllText(req.ScriptPath));

                var statusStr = scope.Contains("status") ? scope.Get<string>("status") : "error";
                var statusText = scope.Contains("status_text") ? scope.Get<string>("status_text") : "Script did not set status_text";
                return new StatusScriptResult(ToolStatusHelper.FromString(statusStr), statusText);
            }
        }
        catch (Exception ex)
        {
            return new StatusScriptResult(ToolStatus.Error, $"Script execution failed: {ex.Message}");
        }
    }

    private static ToolScriptResult RunToolOrViewScriptCore(
        string scriptPath,
        string toolDirectory,
        string? projectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings,
        Action<int>? reportProgress)
    {
        if (!File.Exists(scriptPath))
            return new ToolScriptResult(ToolStatus.Error, $"Script not found: {scriptPath}", true);

        try
        {
            using (Py.GIL())
            {
                using var scope = Py.CreateScope();
                SetCommonVariables(scope, toolDirectory, projectDirectory,
                    intermediateDirectory, outputDirectory, settings, reportProgress);
                scope.Exec(File.ReadAllText(scriptPath));

                var statusStr = scope.Contains("status") ? scope.Get<string>("status") : "error";
                var statusText = scope.Contains("status_text") ? scope.Get<string>("status_text") : "Script did not set status_text";
                var showStatus = scope.Contains("show_status") && scope.Get<bool>("show_status");
                return new ToolScriptResult(ToolStatusHelper.FromString(statusStr), statusText, showStatus);
            }
        }
        catch (Exception ex)
        {
            return new ToolScriptResult(ToolStatus.Error, $"Script execution failed: {ex.Message}", true);
        }
    }

    private static void SetCommonVariables(
        PyModule scope,
        string toolDirectory,
        string? projectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings,
        Action<int>? reportProgress)
    {
        scope.Set("tool_directory", toolDirectory);
        scope.Set("taste_project_directory", projectDirectory ?? string.Empty);
        scope.Set("intermediate_directory", intermediateDirectory ?? string.Empty);
        scope.Set("output_directory", outputDirectory ?? string.Empty);

        var pySettings = new PyList();
        foreach (var (name, value) in settings)
        {
            var tuple = new PyTuple(new PyObject[] { name.ToPython(), value.ToPython() });
            pySettings.Append(tuple);
            tuple.Dispose();
        }
        scope.Set("settings", pySettings);
        pySettings.Dispose();

        if (reportProgress != null)
            scope.Set("report_progress", reportProgress);
    }
}
