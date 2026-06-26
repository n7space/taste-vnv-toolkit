using System;
using System.IO;
using System.Threading.Tasks;
using Xunit;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit_tests;

[Collection("PythonTests")]
public class PythonRunnerStatusTests
{
    private static readonly string ScriptsDir = Path.Combine(
        AppContext.BaseDirectory, "TestData", "scripts");

    private static StatusScriptRequest MakeRequest(string fileName) =>
        new(Path.Combine(ScriptsDir, fileName), ScriptsDir, null, null, null, []);

    [Fact]
    public async Task RunStatusBatchAsync_OkScript_ReturnsOkStatus()
    {
        var results = await PythonRunner.RunStatusBatchAsync([MakeRequest("status_ok.py")]);

        Assert.Equal(ToolStatus.OK, results[0].Status);
        Assert.Equal("Everything is fine", results[0].StatusText);
    }

    [Fact]
    public async Task RunStatusBatchAsync_WarningScript_ReturnsWarningStatus()
    {
        var results = await PythonRunner.RunStatusBatchAsync([MakeRequest("status_warning.py")]);

        Assert.Equal(ToolStatus.Warning, results[0].Status);
        Assert.Equal("Something to watch", results[0].StatusText);
    }

    [Fact]
    public async Task RunStatusBatchAsync_ErrorScript_ReturnsErrorStatus()
    {
        var results = await PythonRunner.RunStatusBatchAsync([MakeRequest("status_error.py")]);

        Assert.Equal(ToolStatus.Error, results[0].Status);
        Assert.Equal("Something went wrong", results[0].StatusText);
    }

    [Fact]
    public async Task RunStatusBatchAsync_MultipleScripts_ReturnsAllInOrder()
    {
        var requests = new[]
        {
            MakeRequest("status_ok.py"),
            MakeRequest("status_warning.py"),
            MakeRequest("status_error.py"),
        };

        var results = await PythonRunner.RunStatusBatchAsync(requests);

        Assert.Equal(3, results.Count);
        Assert.Equal(ToolStatus.OK, results[0].Status);
        Assert.Equal(ToolStatus.Warning, results[1].Status);
        Assert.Equal(ToolStatus.Error, results[2].Status);
    }

    [Fact]
    public async Task RunStatusBatchAsync_MissingScript_ReturnsError()
    {
        var results = await PythonRunner.RunStatusBatchAsync([MakeRequest("nonexistent.py")]);

        Assert.Equal(ToolStatus.Error, results[0].Status);
        Assert.Contains("Script not found", results[0].StatusText);
    }
}
