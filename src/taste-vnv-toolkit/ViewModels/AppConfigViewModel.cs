using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit.ViewModels;

public partial class AppConfigViewModel : ViewModelBase
{
    private readonly ConfigurationOptions _config;
    private readonly Action _saveConfig;
    private readonly List<(string Property, ToolSettingViewModel Vm)> _entries = new();

    public ObservableCollection<ToolSettingViewModel> Settings { get; } = new();

    public event EventHandler? SaveConfirmed;
    public event EventHandler? Cancelled;

    public AppConfigViewModel(ConfigurationOptions config, Action saveConfig)
    {
        _config = config;
        _saveConfig = saveConfig;

        AddEntry("ToolDirectory", "Tool Directory", config.ToolDirectory ?? "");
        AddEntry("ResultDirectory", "Result Directory", config.ResultDirectory ?? "");
        AddEntry("IntermediateDirectory", "Intermediate Directory", config.IntermediateDirectory ?? "");
    }

    private void AddEntry(string property, string label, string value)
    {
        var setting = new ToolSetting { Name = label, Type = SettingType.String };
        var vm = new ToolSettingViewModel(setting, value);
        _entries.Add((property, vm));
        Settings.Add(vm);
    }

    [RelayCommand]
    private void Save()
    {
        foreach (var (prop, vm) in _entries)
        {
            switch (prop)
            {
                case "ToolDirectory": _config.ToolDirectory = vm.StringValue; break;
                case "ResultDirectory": _config.ResultDirectory = vm.StringValue; break;
                case "IntermediateDirectory": _config.IntermediateDirectory = vm.StringValue; break;
            }
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
