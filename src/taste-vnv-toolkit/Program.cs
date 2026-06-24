using Avalonia;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using CommandLine;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit;

sealed class Program
{
    [Verb("gui", HelpText = "Launch GUI")]
    public class GuiOptions
    {
        [Option('c', "configuration-path", Required = false, HelpText = "Configuration file path")]
        public string? OptionsPath { get; set; }

        [Option('p', "project-path", Required = false, HelpText = "TASTE project directory (default: current directory)")]
        public string? ProjectPath { get; set; }
    }

    [Verb("status", HelpText = "Print the status of a tool")]
    public class StatusOptions
    {
        [Option('c', "configuration-path", Required = false, HelpText = "Configuration file path")]
        public string? OptionsPath { get; set; }

        [Option('p', "project-path", Required = false, HelpText = "TASTE project directory (default: current directory)")]
        public string? ProjectPath { get; set; }

        [Value(0, Required = true, MetaName = "tool-name", HelpText = "Name of the tool")]
        public string ToolName { get; set; } = string.Empty;
    }

    [Verb("run", HelpText = "Run a tool")]
    public class RunOptions
    {
        [Option('c', "configuration-path", Required = false, HelpText = "Configuration file path")]
        public string? OptionsPath { get; set; }

        [Option('p', "project-path", Required = false, HelpText = "TASTE project directory (default: current directory)")]
        public string? ProjectPath { get; set; }

        [Value(0, Required = true, MetaName = "tool-name", HelpText = "Name of the tool")]
        public string ToolName { get; set; } = string.Empty;
    }

    // Initialization code. Don't use any Avalonia, third-party APIs or any
    // SynchronizationContext-reliant code before AppMain is called: things aren't initialized
    // yet and stuff might break.
    [STAThread]
    public static void Main(string[] args)
    {
        Parser.Default
            .ParseArguments<GuiOptions, StatusOptions, RunOptions>(args)
            .WithParsed<GuiOptions>(RunGui)
            .WithParsed<StatusOptions>(RunStatus)
            .WithParsed<RunOptions>(RunTool);
    }

    // ── GUI ──────────────────────────────────────────────────────────────────

    private static void RunGui(GuiOptions o)
    {
        Console.WriteLine("Launching GUI...");
        var options_path = o.OptionsPath ?? Constants.DEFAULT_CONFIG_FILE_NAME;
        var project_path = o.ProjectPath ?? Directory.GetCurrentDirectory();
        Console.WriteLine($"options: {options_path}, project: {project_path}");
        BuildAvaloniaApp()
            .StartWithClassicDesktopLifetime([
                options_path,
                project_path
            ]);
    }

    // ── CLI helpers ───────────────────────────────────────────────────────────

    private static ConfigurationOptions LoadConfig(string? path)
    {
        var configPath = path ?? Constants.DEFAULT_CONFIG_FILE_NAME;
        try
        {
            return ConfigurationOptions.Deserialize(
                       new FileStream(configPath, FileMode.Open, FileAccess.Read))
                   ?? new ConfigurationOptions();
        }
        catch
        {
            return new ConfigurationOptions();
        }
    }

    private static (ToolDefinition Definition, string Directory)? FindTool(
        ConfigurationOptions config, string toolName)
    {
        if (string.IsNullOrEmpty(config.ToolDirectory))
        {
            Console.Error.WriteLine("Tool directory is not configured.");
            return null;
        }

        var tools = ToolLoader.LoadAll(config.ToolDirectory);
        var match = tools.Find(t =>
            string.Equals(t.Definition.Name, toolName, StringComparison.OrdinalIgnoreCase));

        if (match == default)
        {
            Console.Error.WriteLine($"Tool not found: {toolName}");
            return null;
        }

        return match;
    }

    private static IEnumerable<(string Name, object Value)> GetSettings(
        ToolDefinition def, ConfigurationOptions config)
    {
        foreach (var setting in def.Settings)
        {
            var entry = config.ToolSettings
                .Find(e => e.ToolName == def.Name && e.SettingName == setting.Name);
            var strValue = entry?.Value ?? setting.DefaultValue;

            object value = setting.Type switch
            {
                SettingType.Bool => bool.TryParse(strValue, out var b) ? b : false,
                SettingType.Int => int.TryParse(strValue, out var i) ? i : 0,
                _ => strValue
            };

            yield return (setting.Name, value);
        }
    }

    // ── status verb ───────────────────────────────────────────────────────────

    private static void RunStatus(StatusOptions o)
    {
        var config = LoadConfig(o.OptionsPath);
        var projectPath = o.ProjectPath ?? Directory.GetCurrentDirectory();
        var found = FindTool(config, o.ToolName);
        if (found is null) { Environment.Exit(1); return; }

        var (def, toolDir) = found.Value;
        var request = new StatusScriptRequest(
            Path.Combine(toolDir, def.StatusScript),
            toolDir, projectPath,
            config.IntermediateDirectory, config.ResultDirectory,
            GetSettings(def, config));

        PythonRunner.Initialize();
        var results = PythonRunner.RunStatusBatchAsync([request])
            .GetAwaiter().GetResult();
        var result = results[0];

        PythonRunner.Shutdown();
        Console.WriteLine($"Status:  {result.Status}");
        Console.WriteLine($"Message: {result.StatusText}");

        Environment.Exit(result.Status == ToolStatus.OK ? 0 : 1);
    }

    // ── run verb ──────────────────────────────────────────────────────────────

    private static void RunTool(RunOptions o)
    {
        var config = LoadConfig(o.OptionsPath);
        var projectPath = o.ProjectPath ?? Directory.GetCurrentDirectory();
        var found = FindTool(config, o.ToolName);
        if (found is null) { Environment.Exit(1); return; }

        var (def, toolDir) = found.Value;
        var scriptPath = Path.Combine(toolDir, def.ToolScript);

        Action<int> progress = n => Console.Write($"\rProgress: {n}%   ");

        PythonRunner.Initialize();
        var result = PythonRunner.RunToolScriptAsync(
            scriptPath, toolDir,
            projectPath, config.IntermediateDirectory,
            config.ResultDirectory, GetSettings(def, config), progress)
            .GetAwaiter().GetResult();

        Console.WriteLine();
        PythonRunner.Shutdown();
        Console.WriteLine($"Status:  {result.Status}");
        Console.WriteLine($"Message: {result.StatusText}");

        Environment.Exit(result.Status == ToolStatus.OK ? 0 : 1);
    }

    // ── Avalonia configuration ────────────────────────────────────────────────

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
#if DEBUG
            .WithDeveloperTools()
#endif
            .WithInterFont()
            .LogToTrace();
}

