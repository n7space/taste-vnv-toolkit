using System.Collections.Generic;
using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;

namespace taste_vnv_toolkit.ViewModels;

public partial class ToolGroupViewModel : ViewModelBase
{
    public string GroupName { get; }
    public ObservableCollection<ToolViewModel> Tools { get; }

    [ObservableProperty]
    private bool _isExpanded = true;

    public ToolGroupViewModel(string groupName, IEnumerable<ToolViewModel> tools)
    {
        GroupName = groupName;
        Tools = new ObservableCollection<ToolViewModel>(tools);
    }
}
