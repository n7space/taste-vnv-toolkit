using System;
using System.IO;
using System.Text;
using Xunit;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit_tests;

public class ConfigurationOptionsTests : IDisposable
{
    private readonly string _tempDir;

    public ConfigurationOptionsTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        Directory.Delete(_tempDir, recursive: true);
    }

    [Fact]
    public void Serialize_ValidOptions_ReturnsTrue()
    {
        var options = new ConfigurationOptions
        {
            ToolDirectory = "/tools",
            ResultDirectory = "/results",
            IntermediateDirectory = "/intermediate"
        };
        using var stream = new MemoryStream();

        var result = ConfigurationOptions.Serialize(options, stream);

        Assert.True(result);
    }

    [Fact]
    public void Serialize_ValidOptions_WritesNonEmptyContent()
    {
        var options = new ConfigurationOptions { ToolDirectory = "/tools" };
        using var stream = new MemoryStream();

        ConfigurationOptions.Serialize(options, stream);

        Assert.True(stream.Length > 0);
    }

    [Fact]
    public void Deserialize_AfterSerialize_RoundTripsDirectories()
    {
        var original = new ConfigurationOptions
        {
            ToolDirectory = "/tools",
            ResultDirectory = "/results",
            IntermediateDirectory = "/intermediate"
        };
        using var stream = new MemoryStream();
        ConfigurationOptions.Serialize(original, stream);
        stream.Position = 0;

        var loaded = ConfigurationOptions.Deserialize(stream);

        Assert.NotNull(loaded);
        Assert.Equal("/tools", loaded.ToolDirectory);
        Assert.Equal("/results", loaded.ResultDirectory);
        Assert.Equal("/intermediate", loaded.IntermediateDirectory);
    }

    [Fact]
    public void Deserialize_AfterSerialize_RoundTripsToolSettings()
    {
        var original = new ConfigurationOptions { ToolDirectory = "/tools" };
        original.ToolSettings.Add(new ToolSettingEntry
        {
            ToolName = "My Tool",
            SettingName = "param1",
            Value = "value1"
        });
        original.ToolSettings.Add(new ToolSettingEntry
        {
            ToolName = "Other Tool",
            SettingName = "count",
            Value = "42"
        });
        using var stream = new MemoryStream();
        ConfigurationOptions.Serialize(original, stream);
        stream.Position = 0;

        var loaded = ConfigurationOptions.Deserialize(stream);

        Assert.NotNull(loaded);
        Assert.Equal(2, loaded.ToolSettings.Count);
        Assert.Equal("My Tool", loaded.ToolSettings[0].ToolName);
        Assert.Equal("param1", loaded.ToolSettings[0].SettingName);
        Assert.Equal("value1", loaded.ToolSettings[0].Value);
        Assert.Equal("Other Tool", loaded.ToolSettings[1].ToolName);
        Assert.Equal("42", loaded.ToolSettings[1].Value);
    }

    [Fact]
    public void Serialize_ThenDeserialize_FileRoundTrip()
    {
        var filePath = Path.Combine(_tempDir, "config.xml");
        var original = new ConfigurationOptions
        {
            ToolDirectory = "/tools",
            ResultDirectory = "/out",
            IntermediateDirectory = "/tmp"
        };

        using (var writeStream = new FileStream(filePath, FileMode.Create, FileAccess.Write))
            ConfigurationOptions.Serialize(original, writeStream);

        using var readStream = new FileStream(filePath, FileMode.Open, FileAccess.Read);
        var loaded = ConfigurationOptions.Deserialize(readStream);

        Assert.NotNull(loaded);
        Assert.Equal("/tools", loaded.ToolDirectory);
        Assert.Equal("/out", loaded.ResultDirectory);
        Assert.Equal("/tmp", loaded.IntermediateDirectory);
    }

    [Fact]
    public void Deserialize_InvalidXml_ReturnsNull()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes("this is not valid xml content"));

        var result = ConfigurationOptions.Deserialize(stream);

        Assert.Null(result);
    }

    [Fact]
    public void Deserialize_EmptyStream_ReturnsNull()
    {
        using var stream = new MemoryStream();

        var result = ConfigurationOptions.Deserialize(stream);

        Assert.Null(result);
    }
}
