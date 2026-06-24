using System;
using Avalonia.Controls;
using Avalonia.Interactivity;
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
        if (DataContext is MainWindowViewModel vm)
            await vm.LoadStatusesAsync();
    }

    private void OnWindowClosed(object? sender, EventArgs e)
    {
        PythonRunner.TryShutdown();
        Environment.Exit(0);
    }
}