using System;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Serilog;
using taste_vnv_toolkit.Models;
using taste_vnv_toolkit.ViewModels;

namespace taste_vnv_toolkit.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        Loaded += OnWindowLoaded;
        Closed += OnWindowClosed;
    }

    private async void OnWindowLoaded(object? sender, RoutedEventArgs e)
    {
        try
        {
            PythonRunner.Initialize();
            if (DataContext is MainWindowViewModel vm)
                await vm.LoadStatusesAsync();
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to load tool statuses during window startup");
        }
    }

    private void OnWindowClosed(object? sender, EventArgs e)
    {
        try
        {
            PythonRunner.Shutdown();
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to shut down Python runtime");
        }
    }
}