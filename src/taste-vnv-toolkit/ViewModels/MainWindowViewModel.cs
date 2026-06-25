using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Diagnostics;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using CommunityToolkit.Mvvm.Input;
using Serilog;
using taste_vnv_toolkit.Models;
using taste_vnv_toolkit.Views;

namespace taste_vnv_toolkit.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    private const uint _optionsPathArgumentIndex = 0;
    private const uint _tasteProjectDirectoryArgumentIndex = 1;
    private readonly string _optionsPath;
    private readonly string _tasteProjectDirectory;
    private readonly List<ToolViewModel> _allTools = new();

    public ConfigurationOptions options { get; set; }
    public ObservableCollection<ToolGroupViewModel> ToolGroups { get; } = new();

    public MainWindowViewModel(string[] args)
    {
        Trace.Assert(args != null && args.Length == 2);
        _optionsPath = args[_optionsPathArgumentIndex];
        _tasteProjectDirectory = args[_tasteProjectDirectoryArgumentIndex];
        options = ConfigurationOptions.Deserialize(
            new FileStream(_optionsPath, FileMode.OpenOrCreate))
             ?? new ConfigurationOptions();

        LoadTools();
    }

    private void LoadTools()
    {
        _allTools.Clear();
        ToolGroups.Clear();

        if (options.ToolDirectory == null || !Directory.Exists(options.ToolDirectory))
            return;

        Action saveConfig = SaveConfig;
        var loadedTools = ToolLoader.LoadAll(options.ToolDirectory);

        foreach (var (definition, toolDir) in loadedTools)
            _allTools.Add(new ToolViewModel(definition, toolDir, _tasteProjectDirectory, options, saveConfig));

        var groups = _allTools
            .GroupBy(t => t.Definition.Group)
            .OrderBy(g => g.Key);

        foreach (var group in groups)
            ToolGroups.Add(new ToolGroupViewModel(group.Key, group.ToList()));
    }

    public async Task LoadStatusesAsync()
    {
        _allTools.ForEach(t => t.ResetStatus());

        var results = await PythonRunner.RunStatusBatchAsync(
            _allTools.Select(t => t.BuildStatusRequest()));

        for (int i = 0; i < results.Count; i++)
            _allTools[i].ApplyStatusResult(results[i]);
    }

    private void SaveConfig()
    {
        try
        {
            ConfigurationOptions.Serialize(options, new FileStream(_optionsPath, FileMode.Create));
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to save configuration");
        }
    }

    [RelayCommand]
    private async Task OpenAppConfig()
    {
        var mainWindow = GetMainWindow();
        if (mainWindow is null) return;

        var vm = new AppConfigViewModel(options, SaveConfig);
        var window = new AppConfigWindow(vm);
        var saved = await window.ShowDialog<bool>(mainWindow);
        if (saved)
            LoadTools();
    }

    private static Window? GetMainWindow() =>
        (Application.Current?.ApplicationLifetime as IClassicDesktopStyleApplicationLifetime)?.MainWindow;
}
