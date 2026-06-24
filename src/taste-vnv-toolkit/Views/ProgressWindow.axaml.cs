using Avalonia.Controls;
using taste_vnv_toolkit.ViewModels;

namespace taste_vnv_toolkit.Views;

public partial class ProgressWindow : Window
{
    public ProgressWindow(ProgressViewModel viewModel)
    {
        DataContext = viewModel;
        InitializeComponent();
    }
}
