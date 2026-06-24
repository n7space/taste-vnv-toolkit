using System;
using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit.ViewModels;

public partial class ToolConfigViewModel : ViewModelBase
{
    private readonly ToolDefinition _definition;
    private readonly ConfigurationOptions _config;
    private readonly Action _saveConfig;

    public string ToolName => _definition.Name;
    public ObservableCollection<ToolSettingViewModel> Settings { get; } = new();

    public event EventHandler? SaveConfirmed;
    public event EventHandler? Cancelled;

    public ToolConfigViewModel(ToolDefinition definition, ConfigurationOptions config, Action saveConfig)
    {
        _definition = definition;
        _config = config;
        _saveConfig = saveConfig;

        foreach (var setting in definition.Settings)
        {
            var entry = config.ToolSettings
                .Find(e => e.ToolName == definition.Name && e.SettingName == setting.Name);
            var currentValue = entry?.Value ?? setting.DefaultValue;
            Settings.Add(new ToolSettingViewModel(setting, currentValue));
        }
    }

    [RelayCommand]
    private void Save()
    {
        foreach (var settingVm in Settings)
        {
            var entry = _config.ToolSettings
                .Find(e => e.ToolName == _definition.Name && e.SettingName == settingVm.Name);

            if (entry == null)
            {
                entry = new ToolSettingEntry
                {
                    ToolName = _definition.Name,
                    SettingName = settingVm.Name
                };
                _config.ToolSettings.Add(entry);
            }

            entry.Value = settingVm.GetStringValue();
        }

        _saveConfig();
        SaveConfirmed?.Invoke(this, EventArgs.Empty);
    }

    [RelayCommand]
    private void Cancel()
    {
        Cancelled?.Invoke(this, EventArgs.Empty);
    }
}
