namespace taste_vnv_toolkit.Models;

using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization;
using System.Xml;
using Serilog;

[DataContract(Namespace = "http://n7space.com/TVnVTK")]
public class ToolSettingEntry
{
    [DataMember]
    public string? ToolName { get; set; }

    [DataMember]
    public string? SettingName { get; set; }

    [DataMember]
    public string? Value { get; set; }
}

[DataContract(Namespace = "http://n7space.com/TVnVTK")]
public class ConfigurationOptions
{
    [DataMember]
    internal string? toolDirectory;

    public string? ToolDirectory { get => toolDirectory; set => toolDirectory = value; }

    [DataMember]
    internal string? resultDirectory;

    public string? ResultDirectory { get => resultDirectory; set => resultDirectory = value; }

    [DataMember]
    internal string? intermediateDirectory;

    public string? IntermediateDirectory { get => intermediateDirectory; set => intermediateDirectory = value; }

    [DataMember]
    private List<ToolSettingEntry>? toolSettings;

    public List<ToolSettingEntry> ToolSettings
    {
        get => toolSettings ??= new List<ToolSettingEntry>();
        set => toolSettings = value;
    }

    public static bool Serialize(ConfigurationOptions options, Stream stream)
    {
        try
        {
            var serializer = new DataContractSerializer(typeof(ConfigurationOptions));
            var settings = new XmlWriterSettings { Indent = true };
            using (var writer = XmlWriter.Create(stream, settings))
            {
                serializer.WriteObject(writer, options);
            }
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Configuration options serialization failed");
            return false;
        }
    }

    public static ConfigurationOptions? Deserialize(Stream stream)
    {
        try
        {
            var serializer = new DataContractSerializer(typeof(ConfigurationOptions));
            var options = serializer.ReadObject(stream) as ConfigurationOptions;
            return options;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Configuration options deserialization failed");
            return null;
        }
    }
}
