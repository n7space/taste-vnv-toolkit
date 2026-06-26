using CommunityToolkit.Mvvm.ComponentModel;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit.ViewModels;

public partial class ToolSettingViewModel : ViewModelBase
{
    private readonly ToolSetting _definition;

    public string Name => _definition.Name;
    public bool IsTextType => _definition.Type != SettingType.Bool;
    public bool IsBoolType => _definition.Type == SettingType.Bool;
    public SettingType Type => _definition.Type;

    [ObservableProperty]
    private string _stringValue = string.Empty;

    [ObservableProperty]
    private bool _boolValue;

    public ToolSettingViewModel(ToolSetting definition, string currentValue)
    {
        _definition = definition;

        if (definition.Type == SettingType.Bool)
            _boolValue = bool.TryParse(currentValue, out var b) ? b : false;
        else
            _stringValue = currentValue;
    }

    public object GetValue()
    {
        return _definition.Type switch
        {
            SettingType.Bool => BoolValue,
            SettingType.Int => int.TryParse(StringValue, out var i) ? i : 0,
            _ => StringValue
        };
    }

    public string GetStringValue()
    {
        return _definition.Type switch
        {
            SettingType.Bool => BoolValue.ToString().ToLowerInvariant(),
            _ => StringValue
        };
    }
}
