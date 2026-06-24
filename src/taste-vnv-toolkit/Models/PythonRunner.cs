using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Python.Runtime;

namespace taste_vnv_toolkit.Models;

public static class PythonRunner
{
    private static bool _initialized = false;
    private static bool _available = false;
    private static readonly object _initLock = new();

    public static bool IsAvailable
    {
        get
        {
            EnsureInitialized();
            return _available;
        }
    }

    private static void EnsureInitialized()
    {
        lock (_initLock)
        {
            if (_initialized) return;
            _initialized = true;
            try
            {
                PythonEngine.Initialize();
                _available = true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Python initialization failed: {ex.Message}");
                _available = false;
            }
        }
    }

    public static void TryShutdown()
    {
        lock (_initLock)
        {
            if (!_initialized || !_available) return;
            try { PythonEngine.Shutdown(); } catch { }
            _available = false;
        }
    }

    public static Task<StatusScriptResult> RunStatusScriptAsync(
        string scriptPath,
        string toolDirectory,
        string? tasteProjectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings)
    {
        return Task.Run(() =>
            RunStatusScript(scriptPath, toolDirectory, tasteProjectDirectory,
                intermediateDirectory, outputDirectory, settings));
    }

    public static Task<ToolScriptResult> RunToolScriptAsync(
        string scriptPath,
        string toolDirectory,
        string? tasteProjectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings,
        Action<int>? reportProgress)
    {
        return Task.Run(() =>
            RunToolOrViewScript(scriptPath, toolDirectory, tasteProjectDirectory,
                intermediateDirectory, outputDirectory, settings, reportProgress));
    }

    public static Task<ToolScriptResult> RunViewScriptAsync(
        string scriptPath,
        string toolDirectory,
        string? tasteProjectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings)
    {
        return Task.Run(() =>
            RunToolOrViewScript(scriptPath, toolDirectory, tasteProjectDirectory,
                intermediateDirectory, outputDirectory, settings, null));
    }

    private static StatusScriptResult RunStatusScript(
        string scriptPath,
        string toolDirectory,
        string? tasteProjectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings)
    {
        if (!IsAvailable)
            return new StatusScriptResult(ToolStatus.Error, "Python runtime not available");
        if (!File.Exists(scriptPath))
            return new StatusScriptResult(ToolStatus.Error, $"Script not found: {scriptPath}");

        try
        {
            using (Py.GIL())
            {
                using var scope = Py.CreateScope();
                SetCommonVariables(scope, toolDirectory, tasteProjectDirectory,
                    intermediateDirectory, outputDirectory, settings, null);

                scope.Exec(File.ReadAllText(scriptPath));

                var statusStr = scope.Contains("status") ? scope.Get<string>("status") : "error";
                var statusText = scope.Contains("status_text")
                    ? scope.Get<string>("status_text") : "Script did not set status_text";

                return new StatusScriptResult(ToolStatusHelper.FromString(statusStr), statusText);
            }
        }
        catch (Exception ex)
        {
            return new StatusScriptResult(ToolStatus.Error, $"Script execution failed: {ex.Message}");
        }
    }

    private static ToolScriptResult RunToolOrViewScript(
        string scriptPath,
        string toolDirectory,
        string? tasteProjectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings,
        Action<int>? reportProgress)
    {
        if (!IsAvailable)
            return new ToolScriptResult(ToolStatus.Error, "Python runtime not available", true);
        if (!File.Exists(scriptPath))
            return new ToolScriptResult(ToolStatus.Error, $"Script not found: {scriptPath}", true);

        try
        {
            using (Py.GIL())
            {
                using var scope = Py.CreateScope();
                SetCommonVariables(scope, toolDirectory, tasteProjectDirectory,
                    intermediateDirectory, outputDirectory, settings, reportProgress);

                scope.Exec(File.ReadAllText(scriptPath));

                var statusStr = scope.Contains("status") ? scope.Get<string>("status") : "error";
                var statusText = scope.Contains("status_text")
                    ? scope.Get<string>("status_text") : "Script did not set status_text";
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
        string? tasteProjectDirectory,
        string? intermediateDirectory,
        string? outputDirectory,
        IEnumerable<(string Name, object Value)> settings,
        Action<int>? reportProgress)
    {
        scope.Set("tool_directory", toolDirectory);
        scope.Set("taste_project_directory", tasteProjectDirectory ?? string.Empty);
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
