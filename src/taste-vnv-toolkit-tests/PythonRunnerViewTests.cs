using System;
using System.IO;
using System.Threading.Tasks;
using Xunit;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit_tests;

[Collection("PythonTests")]
public class PythonRunnerViewTests
{
    private static readonly string ScriptsDir = Path.Combine(
        AppContext.BaseDirectory, "TestData", "scripts");

    [Fact]
    public async Task RunViewScriptAsync_OkScript_ReturnsOkAndDoesNotShowStatus()
    {
        var scriptPath = Path.Combine(ScriptsDir, "view_ok.py");

        var result = await PythonRunner.RunViewScriptAsync(
            scriptPath, ScriptsDir, null, null, null, []);

        Assert.Equal(ToolStatus.OK, result.Status);
        Assert.Equal("Results displayed successfully", result.StatusText);
        Assert.False(result.ShowStatus);
    }

    [Fact]
    public async Task RunViewScriptAsync_WarningScript_ReturnsWarningAndShowsStatus()
    {
        var scriptPath = Path.Combine(ScriptsDir, "view_warning.py");

        var result = await PythonRunner.RunViewScriptAsync(
            scriptPath, ScriptsDir, null, null, null, []);

        Assert.Equal(ToolStatus.Warning, result.Status);
        Assert.Equal("Results may be stale", result.StatusText);
        Assert.True(result.ShowStatus);
    }

    [Fact]
    public async Task RunViewScriptAsync_ErrorScript_ReturnsErrorAndShowsStatus()
    {
        var scriptPath = Path.Combine(ScriptsDir, "view_error.py");

        var result = await PythonRunner.RunViewScriptAsync(
            scriptPath, ScriptsDir, null, null, null, []);

        Assert.Equal(ToolStatus.Error, result.Status);
        Assert.Equal("No results found", result.StatusText);
        Assert.True(result.ShowStatus);
    }

    [Fact]
    public async Task RunViewScriptAsync_MissingScript_ReturnsError()
    {
        var scriptPath = Path.Combine(ScriptsDir, "nonexistent_view.py");

        var result = await PythonRunner.RunViewScriptAsync(
            scriptPath, ScriptsDir, null, null, null, []);

        Assert.Equal(ToolStatus.Error, result.Status);
        Assert.Contains("Script not found", result.StatusText);
    }
}
