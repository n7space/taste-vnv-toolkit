using System;
using Serilog;
using Serilog.Events;

namespace taste_vnv_toolkit;

public enum LogVerbosity
{
    Error,
    Warning,
    Info,
    Debug,
    Verbose
}

public static class Logging
{
    private const string OutputTemplate = "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}";

    public static IDisposable Configure(LogVerbosity verbosity, bool silent = false)
    {
        if (silent)
        {
            Log.Logger = new LoggerConfiguration()
                .MinimumLevel.Fatal()
                .CreateLogger();
        }
        else
        {
            var configuration = new LoggerConfiguration()
                .WriteTo.Console(
                    outputTemplate: OutputTemplate,
                    standardErrorFromLevel: LogEventLevel.Warning);

            Log.Logger = verbosity switch
            {
                LogVerbosity.Error => configuration.MinimumLevel.Error().CreateLogger(),
                LogVerbosity.Warning => configuration.MinimumLevel.Warning().CreateLogger(),
                LogVerbosity.Debug => configuration.MinimumLevel.Debug().CreateLogger(),
                LogVerbosity.Verbose => configuration.MinimumLevel.Verbose().CreateLogger(),
                _ => configuration.MinimumLevel.Information().CreateLogger()
            };
        }

        return new LoggerScope();
    }

    private sealed class LoggerScope : IDisposable
    {
        public void Dispose() => Log.CloseAndFlush();
    }
}