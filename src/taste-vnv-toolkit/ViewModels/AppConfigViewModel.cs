using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit.ViewModels;

public partial class AppConfigViewModel : ViewModelBase
{
    private const string _toolDirectorySetting = "ToolDirectory";
    private const string _resultDirectorySetting = "ResultDirectory";
    private const string _intermediateDirectorySetting = "IntermediateDirectory";

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

        AddEntry(_toolDirectorySetting, "Tool Directory", config.ToolDirectory ?? "");
        AddEntry(_resultDirectorySetting, "Result Directory", config.ResultDirectory ?? "");
        AddEntry(_intermediateDirectorySetting, "Intermediate Directory", config.IntermediateDirectory ?? "");
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
                case _toolDirectorySetting: _config.ToolDirectory = vm.StringValue; break;
                case _resultDirectorySetting: _config.ResultDirectory = vm.StringValue; break;
                case _intermediateDirectorySetting: _config.IntermediateDirectory = vm.StringValue; break;
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
