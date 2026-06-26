using Avalonia.Controls;
using Avalonia.Interactivity;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit.Views;

public partial class StatusResultWindow : Window
{
    private ToolStatus _status;
    private string _statusText = string.Empty;

    public string StatusIcon => ToolStatusHelper.ToIcon(_status);
    public string StatusColor => ToolStatusHelper.ToColor(_status);
    public string StatusText => _statusText;

    public StatusResultWindow()
    {
        DataContext = this;
        InitializeComponent();
    }

    public StatusResultWindow(ToolStatus status, string statusText)
    {
        _status = status;
        _statusText = statusText;
        DataContext = this;
        InitializeComponent();
    }

    private void OkButton_Click(object? sender, RoutedEventArgs e)
    {
        Close();
    }
}
