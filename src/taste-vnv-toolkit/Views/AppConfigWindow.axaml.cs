using Avalonia.Controls;
using taste_vnv_toolkit.ViewModels;

namespace taste_vnv_toolkit.Views;

public partial class AppConfigWindow : Window
{
    public AppConfigWindow()
    {
        InitializeComponent();
    }

    public AppConfigWindow(AppConfigViewModel viewModel)
    {
        DataContext = viewModel;
        viewModel.SaveConfirmed += (_, _) => Close(true);
        viewModel.Cancelled += (_, _) => Close(false);
        InitializeComponent();
    }
}
