using System;
using System.IO;
using Xunit;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit_tests;

public class ToolLoaderTests : IDisposable
{
    private readonly string _tempDir;

    public ToolLoaderTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        Directory.Delete(_tempDir, recursive: true);
    }

    [Fact]
    public void LoadAll_NonExistentDirectory_ReturnsEmpty()
    {
        var result = ToolLoader.LoadAll(Path.Combine(_tempDir, "nonexistent"));

        Assert.Empty(result);
    }

    [Fact]
    public void LoadAll_EmptyDirectory_ReturnsEmpty()
    {
        var result = ToolLoader.LoadAll(_tempDir);

        Assert.Empty(result);
    }

    [Fact]
    public void LoadAll_ValidToolXml_LoadsDefinition()
    {
        var toolDir = Path.Combine(_tempDir, "my-tool");
        Directory.CreateDirectory(toolDir);
        File.WriteAllText(Path.Combine(toolDir, "tool.xml"), """
            <?xml version="1.0" encoding="utf-8"?>
            <ToolDefinition>
              <Name>My Tool</Name>
              <Group>Test Group</Group>
              <Hint>A test tool</Hint>
              <Description>Description text</Description>
              <StatusScript>status.py</StatusScript>
              <ToolScript>tool.py</ToolScript>
              <ViewScript>view.py</ViewScript>
              <Settings>
                <Setting>
                  <Name>param1</Name>
                  <Type>String</Type>
                  <Default>default_val</Default>
                </Setting>
              </Settings>
            </ToolDefinition>
            """);

        var result = ToolLoader.LoadAll(_tempDir);

        Assert.Single(result);
        Assert.Equal("My Tool", result[0].Definition.Name);
        Assert.Equal("Test Group", result[0].Definition.Group);
        Assert.Equal("A test tool", result[0].Definition.Hint);
        Assert.Equal("Description text", result[0].Definition.Description);
        Assert.Equal("status.py", result[0].Definition.StatusScript);
        Assert.Equal("tool.py", result[0].Definition.ToolScript);
        Assert.Equal("view.py", result[0].Definition.ViewScript);
        Assert.Single(result[0].Definition.Settings);
        Assert.Equal("param1", result[0].Definition.Settings[0].Name);
        Assert.Equal(SettingType.String, result[0].Definition.Settings[0].Type);
        Assert.Equal("default_val", result[0].Definition.Settings[0].DefaultValue);
        Assert.Equal(toolDir, result[0].ToolDirectory);
    }

    [Fact]
    public void LoadAll_MultipleTools_ReturnsAll()
    {
        for (int i = 1; i <= 3; i++)
        {
            var toolDir = Path.Combine(_tempDir, $"tool-{i}");
            Directory.CreateDirectory(toolDir);
            File.WriteAllText(Path.Combine(toolDir, "tool.xml"), $"""
                <?xml version="1.0" encoding="utf-8"?>
                <ToolDefinition>
                  <Name>Tool {i}</Name>
                  <Group>Group</Group>
                  <Hint></Hint>
                  <Description></Description>
                  <StatusScript>status.py</StatusScript>
                  <ToolScript>tool.py</ToolScript>
                  <ViewScript>view.py</ViewScript>
                </ToolDefinition>
                """);
        }

        var result = ToolLoader.LoadAll(_tempDir);

        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void LoadAll_SubdirectoryWithoutToolXml_IsSkipped()
    {
        Directory.CreateDirectory(Path.Combine(_tempDir, "no-xml-dir"));

        var toolDir = Path.Combine(_tempDir, "valid-tool");
        Directory.CreateDirectory(toolDir);
        File.WriteAllText(Path.Combine(toolDir, "tool.xml"), """
            <?xml version="1.0" encoding="utf-8"?>
            <ToolDefinition>
              <Name>Valid Tool</Name>
              <Group>G</Group>
              <Hint></Hint>
              <Description></Description>
              <StatusScript>s.py</StatusScript>
              <ToolScript>t.py</ToolScript>
              <ViewScript>v.py</ViewScript>
            </ToolDefinition>
            """);

        var result = ToolLoader.LoadAll(_tempDir);

        Assert.Single(result);
        Assert.Equal("Valid Tool", result[0].Definition.Name);
    }

    [Fact]
    public void LoadAll_ToolWithAllSettingTypes_LoadsTypesCorrectly()
    {
        var toolDir = Path.Combine(_tempDir, "typed-tool");
        Directory.CreateDirectory(toolDir);
        File.WriteAllText(Path.Combine(toolDir, "tool.xml"), """
            <?xml version="1.0" encoding="utf-8"?>
            <ToolDefinition>
              <Name>Typed Tool</Name>
              <Group>G</Group>
              <Hint></Hint>
              <Description></Description>
              <StatusScript>s.py</StatusScript>
              <ToolScript>t.py</ToolScript>
              <ViewScript>v.py</ViewScript>
              <Settings>
                <Setting><Name>str_param</Name><Type>String</Type><Default>hello</Default></Setting>
                <Setting><Name>int_param</Name><Type>Int</Type><Default>42</Default></Setting>
                <Setting><Name>bool_param</Name><Type>Bool</Type><Default>true</Default></Setting>
              </Settings>
            </ToolDefinition>
            """);

        var result = ToolLoader.LoadAll(_tempDir);

        Assert.Single(result);
        var settings = result[0].Definition.Settings;
        Assert.Equal(3, settings.Count);
        Assert.Equal("str_param", settings[0].Name);
        Assert.Equal(SettingType.String, settings[0].Type);
        Assert.Equal("hello", settings[0].DefaultValue);
        Assert.Equal("int_param", settings[1].Name);
        Assert.Equal(SettingType.Int, settings[1].Type);
        Assert.Equal("42", settings[1].DefaultValue);
        Assert.Equal("bool_param", settings[2].Name);
        Assert.Equal(SettingType.Bool, settings[2].Type);
        Assert.Equal("true", settings[2].DefaultValue);
    }
}
