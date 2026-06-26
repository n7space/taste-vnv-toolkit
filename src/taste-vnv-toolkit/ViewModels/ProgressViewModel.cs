using CommunityToolkit.Mvvm.ComponentModel;

namespace taste_vnv_toolkit.ViewModels;

public partial class ProgressViewModel : ViewModelBase
{
    public string ToolName { get; }

    [ObservableProperty]
    private int _progress;

    public ProgressViewModel(string toolName)
    {
        ToolName = toolName;
    }
}
