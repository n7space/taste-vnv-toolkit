using System.IO;
using System.Xml.Serialization;
using Xunit;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit_tests;

public class ToolDefinitionImportPathsTests
{
    [Fact]
    public void ToolDefinition_DeserializesImportPaths()
    {
        // Arrange
        var xmlContent = @"<?xml version=""1.0"" encoding=""utf-8""?>
<ToolDefinition>
  <Name>Test Tool</Name>
  <ImportPaths>
    <Path>../shared</Path>
    <Path>lib</Path>
  </ImportPaths>
</ToolDefinition>";

        // Act
        var serializer = new XmlSerializer(typeof(ToolDefinition));
        ToolDefinition? result;
        using (var reader = new StringReader(xmlContent))
        {
            result = serializer.Deserialize(reader) as ToolDefinition;
        }

        // Assert
        Assert.NotNull(result);
        Assert.Equal(2, result.ImportPaths.Count);
        Assert.Equal("../shared", result.ImportPaths[0]);
        Assert.Equal("lib", result.ImportPaths[1]);
    }
}
