using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using Xunit;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit_tests;

/// <summary>
/// Integration tests that launch the taste-vnv-toolkit executable via the CLI
/// (status and run verbs) and verify exit codes and output.
/// </summary>
public class CliTests : IDisposable
{
    private readonly string _tempDir;
    private readonly string _configPath;
    private readonly string _toolsDir;
    private readonly string _exePath;

    public CliTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(_tempDir);

        _toolsDir = Path.Combine(AppContext.BaseDirectory, "TestData");
        _configPath = Path.Combine(_tempDir, "test_config.xml");
        _exePath = ResolveMainExecutable();

        WriteConfig(_configPath, _toolsDir);
    }

    public void Dispose()
    {
        Directory.Delete(_tempDir, recursive: true);
    }

    // ── status verb ───────────────────────────────────────────────────────────

    [Fact]
    public async Task StatusVerb_ExistingTool_ExitsZeroAndPrintsOk()
    {
        var (exitCode, stdout, _) = await RunCliAsync(
            "status", "-c", _configPath, "CLI Test Tool");

        Assert.Equal(0, exitCode);
        Assert.Contains("OK", stdout, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task StatusVerb_NonExistentTool_ExitsNonZero()
    {
        var (exitCode, _, stderr) = await RunCliAsync(
            "status", "-c", _configPath, "No Such Tool");

        Assert.NotEqual(0, exitCode);
        Assert.Contains("Tool not found", stderr, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task StatusVerb_MissingConfigToolDirectory_ExitsNonZero()
    {
        var emptyConfigPath = Path.Combine(_tempDir, "empty_config.xml");
        WriteConfig(emptyConfigPath, toolDirectory: null);

        var (exitCode, _, stderr) = await RunCliAsync(
            "status", "-c", emptyConfigPath, "CLI Test Tool");

        Assert.NotEqual(0, exitCode);
        Assert.Contains("Tool directory is not configured", stderr, StringComparison.OrdinalIgnoreCase);
    }

    // ── run verb ──────────────────────────────────────────────────────────────

    [Fact]
    public async Task RunVerb_ExistingTool_ExitsZeroAndPrintsOk()
    {
        var (exitCode, stdout, _) = await RunCliAsync(
            "run", "-c", _configPath, "CLI Test Tool");

        Assert.Equal(0, exitCode);
        Assert.Contains("OK", stdout, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task RunVerb_NonExistentTool_ExitsNonZero()
    {
        var (exitCode, _, stderr) = await RunCliAsync(
            "run", "-c", _configPath, "No Such Tool");

        Assert.NotEqual(0, exitCode);
        Assert.Contains("Tool not found", stderr, StringComparison.OrdinalIgnoreCase);
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private static string ResolveMainExecutable()
    {
        // AppContext.BaseDirectory = .../src/taste-vnv-toolkit-tests/bin/{config}/net10.0/
        var netDir = AppContext.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar);
        var configDir = Path.GetDirectoryName(netDir)!;        // .../bin/{config}
        var buildConfig = Path.GetFileName(configDir);          // Debug | Release
        var binDir = Path.GetDirectoryName(configDir)!;        // .../bin
        var testProjectDir = Path.GetDirectoryName(binDir)!;   // .../taste-vnv-toolkit-tests
        var srcDir = Path.GetDirectoryName(testProjectDir)!;   // .../src

        return Path.Combine(srcDir, "taste-vnv-toolkit", "bin", buildConfig, "net10.0",
            "taste-vnv-toolkit");
    }

    private static void WriteConfig(string configPath, string? toolDirectory)
    {
        var options = new ConfigurationOptions { ToolDirectory = toolDirectory };
        using var stream = new FileStream(configPath, FileMode.Create, FileAccess.Write);
        ConfigurationOptions.Serialize(options, stream);
    }

    private async Task<(int ExitCode, string Stdout, string Stderr)> RunCliAsync(
        params string[] args)
    {
        var psi = new ProcessStartInfo(_exePath)
        {
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            WorkingDirectory = _tempDir
        };
        foreach (var arg in args)
            psi.ArgumentList.Add(arg);

        using var process = Process.Start(psi)
            ?? throw new InvalidOperationException($"Failed to start process: {_exePath}");

        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();

        await process.WaitForExitAsync();

        return (process.ExitCode, await stdoutTask, await stderrTask);
    }
}
