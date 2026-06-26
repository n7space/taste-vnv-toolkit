using Avalonia.Controls;
using Avalonia.Interactivity;

namespace taste_vnv_toolkit.Views;

public partial class HelpWindow : Window
{
    private string _toolName = string.Empty;
    private string _description = string.Empty;

    public string ToolName => _toolName;
    public string Description => _description;

    public HelpWindow()
    {
        DataContext = this;
        InitializeComponent();
    }

    public HelpWindow(string toolName, string description)
    {
        _toolName = toolName;
        _description = description;
        DataContext = this;
        InitializeComponent();
    }

    private void OkButton_Click(object? sender, RoutedEventArgs e)
    {
        Close();
    }
}
