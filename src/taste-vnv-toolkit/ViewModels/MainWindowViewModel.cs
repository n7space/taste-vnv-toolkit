using System.Diagnostics;
using System.IO;
using System.Reflection;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    public string Greeting { get; set;} = "Welcome to Avalonia!";

    public ConfigurationOptions options {get;set;}

    public MainWindowViewModel(string[] args)
    {
        // First and only argument is the path to options; use of standard args after parsing
        // is chosen to avoid creating static fields or complex passing mechanisms
        Trace.Assert(args != null && args.Length == 1);
        var options_path = args[0];
        options = ConfigurationOptions.Deserialize(
            new FileStream(options_path, FileMode.OpenOrCreate))
             ?? new ConfigurationOptions();
        
        //options.ToolDirectory = "/home/taste/dummy";
        //ConfigurationOptions.Serialize(options, new FileStream(options_path, FileMode.Create));

    }
}
