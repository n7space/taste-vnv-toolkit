using System.Xml.Serialization;

namespace taste_vnv_toolkit.Models;

public enum SettingType
{
    String,
    Int,
    Bool
}

[XmlRoot("Setting")]
public class ToolSetting
{
    [XmlElement("Name")]
    public string Name { get; set; } = string.Empty;

    [XmlElement("Type")]
    public SettingType Type { get; set; } = SettingType.String;

    [XmlElement("Default")]
    public string DefaultValue { get; set; } = string.Empty;
}
