using System;
using System.Collections.Generic;
using System.IO;
using System.Xml.Serialization;

namespace taste_vnv_toolkit.Models;

public static class ToolLoader
{
    public const string ToolDefinitionFileName = "tool.xml";

    /// <summary>
    /// Loads all tool definitions from subdirectories of the given tool directory.
    /// Returns a list of (definition, toolDirectory) pairs.
    /// </summary>
    public static List<(ToolDefinition Definition, string ToolDirectory)> LoadAll(string toolsRootDirectory)
    {
        var result = new List<(ToolDefinition, string)>();

        if (!Directory.Exists(toolsRootDirectory))
            return result;

        var serializer = new XmlSerializer(typeof(ToolDefinition));

        foreach (var subDir in Directory.GetDirectories(toolsRootDirectory))
        {
            var xmlPath = Path.Combine(subDir, ToolDefinitionFileName);
            if (!File.Exists(xmlPath))
                continue;

            try
            {
                using var stream = new FileStream(xmlPath, FileMode.Open, FileAccess.Read);
                var definition = serializer.Deserialize(stream) as ToolDefinition;
                if (definition != null)
                    result.Add((definition, subDir));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to load tool from {xmlPath}: {ex.Message}");
            }
        }

        return result;
    }
}
