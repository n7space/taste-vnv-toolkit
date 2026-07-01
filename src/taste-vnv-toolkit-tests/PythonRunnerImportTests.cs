using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Xunit;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit_tests;

/// <summary>
/// Tests that Python scripts can import modules from their tool directory.
/// </summary>
[Collection("PythonTests")]
public class PythonRunnerImportTests
{
    private static readonly string ScriptsDir = Path.Combine(
        AppContext.BaseDirectory, "TestData", "scripts");

    private static StatusScriptRequest MakeStatusRequest(string fileName) =>
        new(Path.Combine(ScriptsDir, fileName), ScriptsDir, null, null, null, []);

    [Fact]
    public async Task StatusScript_CanImportFromToolDirectory()
    {
        // Arrange & Act
        var results = await PythonRunner.RunStatusBatchAsync([
            MakeStatusRequest("status_with_import.py")
        ]);

        // Assert
        Assert.Single(results);
        Assert.Equal(ToolStatus.OK, results[0].Status);
        Assert.Equal("Value is low", results[0].StatusText);
    }

    [Fact]
    public async Task StatusScript_CanImportAndComputeWarning()
    {
        // Arrange & Act
        var results = await PythonRunner.RunStatusBatchAsync([
            MakeStatusRequest("status_with_import_warning.py")
        ]);

        // Assert
        Assert.Single(results);
        Assert.Equal(ToolStatus.Warning, results[0].Status);
        Assert.Equal("Value is moderate", results[0].StatusText);
    }

    [Fact]
    public async Task MultipleStatusScripts_CanImportIndependently()
    {
        // Arrange
        var requests = new[]
        {
            MakeStatusRequest("status_with_import.py"),
            MakeStatusRequest("status_with_import_warning.py"),
            MakeStatusRequest("status_ok.py"), // Regular script without imports
        };

        // Act
        var results = await PythonRunner.RunStatusBatchAsync(requests);

        // Assert
        Assert.Equal(3, results.Count);
        Assert.Equal(ToolStatus.OK, results[0].Status);
        Assert.Equal(ToolStatus.Warning, results[1].Status);
        Assert.Equal(ToolStatus.OK, results[2].Status);
    }

    [Fact]
    public async Task ToolScript_CanImportFromToolDirectory()
    {
        // Arrange
        var scriptPath = Path.Combine(ScriptsDir, "tool_with_import.py");

        // Act
        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, ScriptsDir, null, null, null, [], null);

        // Assert
        Assert.Equal(ToolStatus.OK, result.Status);
        Assert.Contains("Hello from shared module", result.StatusText);
        Assert.Contains("Parsed: test data", result.StatusText);
        Assert.True(result.ShowStatus);
    }

    [Fact]
    public async Task ViewScript_CanImportFromToolDirectory()
    {
        // Arrange
        var scriptPath = Path.Combine(ScriptsDir, "view_with_import.py");

        // Act
        var result = await PythonRunner.RunViewScriptAsync(
            scriptPath, ScriptsDir, null, null, null, []);

        // Assert
        Assert.Equal(ToolStatus.OK, result.Status);
        Assert.Contains("Hello from shared module", result.StatusText);
        Assert.Contains("Parsed: view data", result.StatusText);
        Assert.True(result.ShowStatus);
    }

    [Fact]
    public async Task StatusScript_CanImportFromCustomImportPath()
    {
        // Arrange - Load tool definition to get custom import paths
        var toolDir = Path.Combine(ScriptsDir, "with_custom_import");
        var toolXmlPath = Path.Combine(toolDir, "tool.xml");

        ToolDefinition? toolDef = null;
        using (var stream = new FileStream(toolXmlPath, FileMode.Open, FileAccess.Read, FileShare.Read))
        {
            var serializer = new System.Xml.Serialization.XmlSerializer(typeof(ToolDefinition));
            toolDef = serializer.Deserialize(stream) as ToolDefinition;
        }

        Assert.NotNull(toolDef);
        Assert.Single(toolDef.ImportPaths);
        Assert.Equal("lib", toolDef.ImportPaths[0]);

        var scriptPath = Path.Combine(toolDir, "status_custom_import.py");
        var request = new StatusScriptRequest(
            scriptPath, toolDir, null, null, null, [], toolDef.ImportPaths);

        // Act
        var results = await PythonRunner.RunStatusBatchAsync([request]);

        // Assert
        Assert.Single(results);
        Assert.Equal(ToolStatus.OK, results[0].Status);
        Assert.Equal("Loaded from custom import path", results[0].StatusText);
    }
}
