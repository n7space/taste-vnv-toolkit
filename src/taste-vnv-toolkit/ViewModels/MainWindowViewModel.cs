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
using taste_vnv_toolkit.Models;
using taste_vnv_toolkit.Views;

namespace taste_vnv_toolkit.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    private readonly string _optionsPath;
    private readonly List<ToolViewModel> _allTools = new();

    public ConfigurationOptions options { get; set; }
    public ObservableCollection<ToolGroupViewModel> ToolGroups { get; } = new();

    public MainWindowViewModel(string[] args)
    {
        Trace.Assert(args != null && args.Length == 1);
        _optionsPath = args[0];
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
            _allTools.Add(new ToolViewModel(definition, toolDir, options, saveConfig));

        var groups = _allTools
            .GroupBy(t => t.Definition.Group)
            .OrderBy(g => g.Key);

        foreach (var group in groups)
            ToolGroups.Add(new ToolGroupViewModel(group.Key, group.ToList()));
    }

    public async Task LoadStatusesAsync()
    {
        var tasks = _allTools.Select(t => t.LoadStatusAsync());
        await Task.WhenAll(tasks);
    }

    private void SaveConfig()
    {
        try
        {
            ConfigurationOptions.Serialize(options, new FileStream(_optionsPath, FileMode.Create));
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to save configuration: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task OpenAppConfig()
    {
        var vm = new AppConfigViewModel(options, SaveConfig);
        var window = new AppConfigWindow(vm);
        var saved = await window.ShowDialog<bool>(GetMainWindow());
        if (saved)
            LoadTools();
    }

    private static Window? GetMainWindow() =>
        (Application.Current?.ApplicationLifetime as IClassicDesktopStyleApplicationLifetime)?.MainWindow;
}
