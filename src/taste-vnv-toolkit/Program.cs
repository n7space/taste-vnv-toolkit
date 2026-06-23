using Avalonia;
using System;
using CommandLine;
using CommandLine.Text;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit;

sealed class Program
{

    [Verb("gui", HelpText= "Launch GUI")]
    public class GuiOptions
    {
        [Option('c', "configuration-path", Required = false, HelpText = "Configuration file path")]
        public string? OptionsPath {get;set;}
    }

    // Initialization code. Don't use any Avalonia, third-party APIs or any
    // SynchronizationContext-reliant code before AppMain is called: things aren't initialized
    // yet and stuff might break.
    [STAThread]
    public static void Main(string[] args)
    {
        Parser.Default.ParseArguments<GuiOptions>(args).WithParsed<GuiOptions>(o =>
        {
            Console.WriteLine("Launching GUI...");
            BuildAvaloniaApp()
                .StartWithClassicDesktopLifetime([o.OptionsPath ?? Constants.DEFAULT_CONFIG_FILE_NAME]);
        });
    } 
    // Avalonia configuration, don't remove; also used by visual designer.
    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
#if DEBUG
            .WithDeveloperTools()
#endif
            .WithInterFont()
            .LogToTrace();
}
