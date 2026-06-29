using Avalonia;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using CommandLine;
using Serilog;
using taste_vnv_toolkit.Models;

namespace taste_vnv_toolkit;

sealed class Program
{
    public abstract class LoggingOptions
    {
        [Option('v', "verbosity", Required = false, HelpText = "Console log verbosity")]
        public LogVerbosity Verbosity { get; set; } = LogVerbosity.Info;
    }

    [Verb("gui", HelpText = "Launch GUI")]
    public class GuiOptions : LoggingOptions
    {
        [Option('c', "configuration-path", Required = false, HelpText = "Configuration file path")]
        public string? OptionsPath { get; set; }

        [Option('p', "project-path", Required = false, HelpText = "TASTE project directory (default: current directory)")]
        public string? ProjectPath { get; set; }
    }

    [Verb("status", HelpText = "Print the status of a tool")]
    public class StatusOptions : LoggingOptions
    {
        [Option('c', "configuration-path", Required = false, HelpText = "Configuration file path")]
        public string? OptionsPath { get; set; }

        [Option('p', "project-path", Required = false, HelpText = "TASTE project directory (default: current directory)")]
        public string? ProjectPath { get; set; }

        [Value(0, Required = true, MetaName = "tool-name", HelpText = "Name of the tool")]
        public string ToolName { get; set; } = string.Empty;
    }

    [Verb("run", HelpText = "Run a tool")]
    public class RunOptions : LoggingOptions
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
    public static int Main(string[] args)
    {
        return Parser.Default
            .ParseArguments<GuiOptions, StatusOptions, RunOptions>(args)
            .MapResult<GuiOptions, StatusOptions, RunOptions, int>(
                RunGui,
                RunStatus,
                RunTool,
                _ => 1);
    }

    // ── GUI ──────────────────────────────────────────────────────────────────

    private static int RunGui(GuiOptions o)
    {
        using var _ = Logging.Configure(o.Verbosity);

        var optionsPath = o.OptionsPath ?? Constants.DEFAULT_CONFIG_FILE_NAME;
        var projectPath = o.ProjectPath ?? Directory.GetCurrentDirectory();

        Log.Information("Launching GUI");
        Log.Information("Options path: {OptionsPath}, project path: {ProjectPath}", optionsPath, projectPath);

        BuildAvaloniaApp()
            .StartWithClassicDesktopLifetime([
                optionsPath,
                projectPath
            ]);

        return 0;
    }

    // ── CLI helpers ───────────────────────────────────────────────────────────

    private static ConfigurationOptions LoadConfig(string? path)
    {
        var configPath = path ?? Constants.DEFAULT_CONFIG_FILE_NAME;
        if (!File.Exists(configPath))
            return new ConfigurationOptions();

        try
        {
            using var stream = new FileStream(configPath, FileMode.Open, FileAccess.Read, FileShare.Read);
            return ConfigurationOptions.Deserialize(stream) ?? new ConfigurationOptions();
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
            Log.Error("Tool directory is not configured.");
            return null;
        }

        var tools = ToolLoader.LoadAll(config.ToolDirectory);
        var match = tools.Find(t =>
            string.Equals(t.Definition.Name, toolName, StringComparison.OrdinalIgnoreCase));

        if (match == default)
        {
            Log.Error("Tool not found: {ToolName}", toolName);
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

    private static int RunStatus(StatusOptions o)
    {
        using var _ = Logging.Configure(o.Verbosity);

        var config = LoadConfig(o.OptionsPath);
        var projectPath = o.ProjectPath ?? Directory.GetCurrentDirectory();
        var found = FindTool(config, o.ToolName);
        if (found is null) { return 1; }

        var (def, toolDir) = found.Value;
        var request = new StatusScriptRequest(
            Path.Combine(toolDir, def.StatusScript),
            toolDir, projectPath,
            config.IntermediateDirectory, config.ResultDirectory,
            GetSettings(def, config), def.ImportPaths);

        PythonRunner.Initialize();
        var results = PythonRunner.RunStatusBatchAsync([request])
            .GetAwaiter().GetResult();
        var result = results[0];

        PythonRunner.Shutdown();
        Log.Information("Status: {Status}", result.Status);
        Log.Information("Message: {Message}", result.StatusText);

        return result.Status == ToolStatus.OK ? 0 : 1;
    }

    // ── run verb ──────────────────────────────────────────────────────────────

    private static int RunTool(RunOptions o)
    {
        using var _ = Logging.Configure(o.Verbosity);

        var config = LoadConfig(o.OptionsPath);
        var projectPath = o.ProjectPath ?? Directory.GetCurrentDirectory();
        var found = FindTool(config, o.ToolName);
        if (found is null) { return 1; }

        var (def, toolDir) = found.Value;
        var scriptPath = Path.Combine(toolDir, def.ToolScript);

        Action<int> progress = n => Log.Information("Progress: {Progress}%", n);

        PythonRunner.Initialize();
        var result = PythonRunner.RunToolScriptAsync(
            scriptPath, toolDir,
            projectPath, config.IntermediateDirectory,
            config.ResultDirectory, GetSettings(def, config), progress, def.ImportPaths)
            .GetAwaiter().GetResult();

        PythonRunner.Shutdown();
        Log.Information("Status: {Status}", result.Status);
        Log.Information("Message: {Message}", result.StatusText);

        return result.Status == ToolStatus.OK ? 0 : 1;
    }

    // ── Avalonia configuration ────────────────────────────────────────────────

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .WithInterFont()
            .LogToTrace();
}

