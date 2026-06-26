using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Xunit;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit_tests;

[Collection("PythonTests")]
public class PythonRunnerToolTests
{
    private static readonly string ScriptsDir = Path.Combine(
        AppContext.BaseDirectory, "TestData", "scripts");

    [Fact]
    public async Task RunToolScriptAsync_OkScript_ShowStatus_ReturnsOkAndShowsStatus()
    {
        var scriptPath = Path.Combine(ScriptsDir, "tool_ok_show.py");

        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, ScriptsDir, null, null, null, [], null);

        Assert.Equal(ToolStatus.OK, result.Status);
        Assert.Equal("Tool completed successfully", result.StatusText);
        Assert.True(result.ShowStatus);
    }

    [Fact]
    public async Task RunToolScriptAsync_OkScript_NoShow_ReturnsOkAndDoesNotShowStatus()
    {
        var scriptPath = Path.Combine(ScriptsDir, "tool_ok_noshow.py");

        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, ScriptsDir, null, null, null, [], null);

        Assert.Equal(ToolStatus.OK, result.Status);
        Assert.Equal("Results presented externally", result.StatusText);
        Assert.False(result.ShowStatus);
    }

    [Fact]
    public async Task RunToolScriptAsync_WarningScript_ReturnsWarningAndShowsStatus()
    {
        var scriptPath = Path.Combine(ScriptsDir, "tool_warning.py");

        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, ScriptsDir, null, null, null, [], null);

        Assert.Equal(ToolStatus.Warning, result.Status);
        Assert.Equal("Tool finished with warnings", result.StatusText);
        Assert.True(result.ShowStatus);
    }

    [Fact]
    public async Task RunToolScriptAsync_ErrorScript_ReturnsErrorAndShowsStatus()
    {
        var scriptPath = Path.Combine(ScriptsDir, "tool_error.py");

        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, ScriptsDir, null, null, null, [], null);

        Assert.Equal(ToolStatus.Error, result.Status);
        Assert.Equal("Tool execution failed", result.StatusText);
        Assert.True(result.ShowStatus);
    }

    [Fact]
    public async Task RunToolScriptAsync_ScriptCallsReportProgress_ProgressIsReported()
    {
        var scriptPath = Path.Combine(ScriptsDir, "tool_with_progress.py");
        var reportedValues = new List<int>();

        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, ScriptsDir, null, null, null, [],
            progress => reportedValues.Add(progress));

        Assert.Equal(ToolStatus.OK, result.Status);
        Assert.Equal([10, 50, 90, 100], reportedValues);
    }

    [Fact]
    public async Task RunToolScriptAsync_ScriptDoesNotCallReportProgress_NothingReported()
    {
        var scriptPath = Path.Combine(ScriptsDir, "tool_no_progress.py");
        var reportedValues = new List<int>();

        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, ScriptsDir, null, null, null, [],
            progress => reportedValues.Add(progress));

        Assert.Equal(ToolStatus.OK, result.Status);
        Assert.Empty(reportedValues);
    }

    [Fact]
    public async Task RunToolScriptAsync_MissingScript_ReturnsError()
    {
        var scriptPath = Path.Combine(ScriptsDir, "nonexistent_tool.py");

        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, ScriptsDir, null, null, null, [], null);

        Assert.Equal(ToolStatus.Error, result.Status);
        Assert.Contains("Script not found", result.StatusText);
    }
}
