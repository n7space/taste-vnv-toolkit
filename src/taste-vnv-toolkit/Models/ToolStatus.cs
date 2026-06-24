namespace taste_vnv_toolkit.Models;

public enum ToolStatus
{
    Unknown,
    OK,
    Warning,
    Error
}

public static class ToolStatusHelper
{
    public static ToolStatus FromString(string? s) => s?.ToLowerInvariant() switch
    {
        "ok" => ToolStatus.OK,
        "warning" => ToolStatus.Warning,
        "error" => ToolStatus.Error,
        _ => ToolStatus.Unknown
    };

    public static string ToIcon(ToolStatus status) => status switch
    {
        ToolStatus.OK => "✓",
        ToolStatus.Warning => "⚠",
        ToolStatus.Error => "✗",
        _ => "○"
    };

    public static string ToColor(ToolStatus status) => status switch
    {
        ToolStatus.OK => "#4CAF50",
        ToolStatus.Warning => "#FF9800",
        ToolStatus.Error => "#F44336",
        _ => "#9E9E9E"
    };
}

public record StatusScriptResult(ToolStatus Status, string StatusText);

public record ToolScriptResult(ToolStatus Status, string StatusText, bool ShowStatus);
