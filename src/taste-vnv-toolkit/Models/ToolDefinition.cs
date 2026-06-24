using System.Collections.Generic;
using System.Xml.Serialization;

namespace taste_vnv_toolkit.Models;

[XmlRoot("ToolDefinition")]
public class ToolDefinition
{
    [XmlElement("Name")]
    public string Name { get; set; } = string.Empty;

    [XmlElement("Group")]
    public string Group { get; set; } = string.Empty;

    [XmlElement("Hint")]
    public string Hint { get; set; } = string.Empty;

    [XmlElement("Description")]
    public string Description { get; set; } = string.Empty;

    [XmlElement("StatusScript")]
    public string StatusScript { get; set; } = string.Empty;

    [XmlElement("ToolScript")]
    public string ToolScript { get; set; } = string.Empty;

    [XmlElement("ViewScript")]
    public string ViewScript { get; set; } = string.Empty;

    [XmlArray("Settings")]
    [XmlArrayItem("Setting")]
    public List<ToolSetting> Settings { get; set; } = new();
}
