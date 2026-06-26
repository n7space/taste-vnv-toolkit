using Avalonia.Controls;
using taste_vnv_toolkit.Models;
using taste_vnv_toolkit.ViewModels;

namespace taste_vnv_toolkit.Views;

public partial class ToolConfigWindow : Window
{
    public ToolConfigWindow()
    {
        DataContext = new ToolConfigViewModel(new ToolDefinition(), new ConfigurationOptions(), () => { });
        InitializeComponent();
    }

    public ToolConfigWindow(ToolConfigViewModel viewModel)
    {
        DataContext = viewModel;
        viewModel.SaveConfirmed += (_, _) => Close(true);
        viewModel.Cancelled += (_, _) => Close(false);
        InitializeComponent();
    }
}
