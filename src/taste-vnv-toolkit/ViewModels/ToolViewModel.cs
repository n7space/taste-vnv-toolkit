using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Threading;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using taste_vnv_toolkit.Models;
using taste_vnv_toolkit.Views;

namespace taste_vnv_toolkit.ViewModels;

public partial class ToolViewModel : ViewModelBase
{
    private readonly ToolDefinition _definition;
    private readonly string _toolDirectory;
    private readonly string _tasteProjectDirectory;
    private readonly ConfigurationOptions _config;
    private readonly Action _saveConfig;

    public string Name => _definition.Name;
    public string Hint => _definition.Hint;
    public ToolDefinition Definition => _definition;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(StatusIcon))]
    [NotifyPropertyChangedFor(nameof(StatusColor))]
    private ToolStatus _status = ToolStatus.Unknown;

    [ObservableProperty]
    private string _statusText = "Loading…";

    public string StatusIcon => ToolStatusHelper.ToIcon(Status);
    public string StatusColor => ToolStatusHelper.ToColor(Status);

    public ToolViewModel(ToolDefinition definition, string toolDirectory,
        string tasteProjectDirectory, ConfigurationOptions config, Action saveConfig)
    {
        _definition = definition;
        _toolDirectory = toolDirectory;
        _tasteProjectDirectory = tasteProjectDirectory;
        _config = config;
        _saveConfig = saveConfig;
    }

    // ── Status helpers used by MainWindowViewModel for batch loading ──────────

    /// <summary>Returns the parameters needed to run this tool's status script.</summary>
    public StatusScriptRequest BuildStatusRequest() => new(
        Path.Combine(_toolDirectory, _definition.StatusScript),
        _toolDirectory,
        _tasteProjectDirectory,
        _config.IntermediateDirectory,
        _config.ResultDirectory,
        GetCurrentSettings());

    /// <summary>Applies a status-script result to the observable properties.</summary>
    public void ApplyStatusResult(StatusScriptResult result)
    {
        Status = result.Status;
        StatusText = result.StatusText;
    }

    /// <summary>Resets the status to the "loading" state.</summary>
    public void ResetStatus()
    {
        Status = ToolStatus.Unknown;
        StatusText = "Loading\u2026";
    }

    /// <summary>
    /// Convenience overload: opens a dedicated Python session for this single
    /// tool.  Prefer <see cref="MainWindowViewModel.LoadStatusesAsync"/> for
    /// batch loading all tools at startup.
    /// </summary>
    public async Task LoadStatusAsync()
    {
        ResetStatus();
        var results = await PythonRunner.RunStatusBatchAsync([BuildStatusRequest()]);
        ApplyStatusResult(results[0]);
    }

    [RelayCommand]
    private async Task ShowHelp()
    {
        var dialog = new HelpWindow(_definition.Name, _definition.Description);
        await dialog.ShowDialog(GetMainWindow());
    }

    [RelayCommand]
    private async Task Configure()
    {
        var configVm = new ToolConfigViewModel(_definition, _config, _saveConfig);
        var window = new ToolConfigWindow(configVm);
        await window.ShowDialog(GetMainWindow());
    }

    [RelayCommand]
    private async Task View()
    {
        var scriptPath = Path.Combine(_toolDirectory, _definition.ViewScript);
        var result = await PythonRunner.RunViewScriptAsync(
            scriptPath, _toolDirectory,
            _tasteProjectDirectory, _config.IntermediateDirectory,
            _config.ResultDirectory, GetCurrentSettings());

        if (result.ShowStatus)
            await ShowStatusResultAsync(result.Status, result.StatusText);
    }

    [RelayCommand]
    private async Task RunTool()
    {
        bool progressWindowShown = false;
        var progressVm = new ProgressViewModel(_definition.Name);
        var progressWindow = new ProgressWindow(progressVm);

        Action<int> progressCallback = n =>
        {
            Dispatcher.UIThread.Post(() =>
            {
                if (!progressWindowShown)
                {
                    progressWindowShown = true;
                    progressWindow.Show();
                }
                progressVm.Progress = n;
            });
        };

        var scriptPath = Path.Combine(_toolDirectory, _definition.ToolScript);
        var result = await PythonRunner.RunToolScriptAsync(
            scriptPath, _toolDirectory,
            _tasteProjectDirectory, _config.IntermediateDirectory,
            _config.ResultDirectory, GetCurrentSettings(), progressCallback);

        if (progressWindowShown)
            progressWindow.Close();

        if (result.ShowStatus)
            await ShowStatusResultAsync(result.Status, result.StatusText);
    }

    private static async Task ShowStatusResultAsync(ToolStatus status, string statusText)
    {
        var dialog = new StatusResultWindow(status, statusText);
        await dialog.ShowDialog(GetMainWindow());
    }

    private IEnumerable<(string Name, object Value)> GetCurrentSettings()
    {
        foreach (var setting in _definition.Settings)
        {
            var entry = _config.ToolSettings
                .Find(e => e.ToolName == _definition.Name && e.SettingName == setting.Name);
            var strValue = entry?.Value ?? setting.DefaultValue;

            object value = setting.Type switch
            {
                SettingType.Bool => bool.TryParse(strValue, out var b) ? b : false,
                SettingType.Int => int.TryParse(strValue, out var i) ? i : 0,
                _ => strValue
            };

            yield return (setting.Name, value);
        }
    }

    private static Window GetMainWindow() =>
        (Application.Current?.ApplicationLifetime as IClassicDesktopStyleApplicationLifetime)?.MainWindow
        ?? throw new InvalidOperationException("Main window is not available");
}
