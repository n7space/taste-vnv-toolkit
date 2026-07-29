"""
Shared utilities for Ceedling test tools.
"""

import os
import re
import shutil

from vnvtoolkit import get_setting, resolve_path


# ── Settings utilities ────────────────────────────────────────────────────────

def get_ceedling_command(settings):
    """Get the configured ceedling command."""
    return str(get_setting(settings, "Ceedling command", "ceedling"))


def check_ceedling_available(ceedling_command):
    """Check if ceedling is available in PATH."""
    path = shutil.which(ceedling_command)
    if path is not None:
        return "ok", f"{ceedling_command} found at {path}"
    else:
        return "error", f"{ceedling_command} not found in PATH"


# ── Progress reporting ────────────────────────────────────────────────────────

def emit_progress(value):
    """Report progress if the callback is available."""
    if "report_progress" in globals():
        report_progress(value)


# ── Project.yml parsing ───────────────────────────────────────────────────────

def parse_project_yml(project_yml_path):
    """Parse project.yml to extract build_root and test directory."""
    build_root = "build"
    test_directory = "test"
    
    if not os.path.isfile(project_yml_path):
        return build_root, test_directory
    
    try:
        with open(project_yml_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract :build_root: value
        build_root_match = re.search(r'^\s*:build_root:\s*(.+?)\s*$', content, re.MULTILINE)
        if build_root_match:
            build_root = build_root_match.group(1).strip()
        
        # Extract first :test: path (format: - +:test/** or - test/**)
        test_path_match = re.search(r'^\s*:test:\s*$\s*^\s*-\s*\+?:?(.+?)(?:/\*\*)?(?:\s|$)', content, re.MULTILINE)
        if test_path_match:
            test_directory = test_path_match.group(1).strip()
    
    except Exception:
        # If parsing fails, use defaults
        pass
    
    return build_root, test_directory


# ── Path operations and validation ────────────────────────────────────────────

def summarize_directory(directory_path):
    """Create a summary of directory contents for error messages."""
    if not os.path.isdir(directory_path):
        return "directory does not exist"

    entries = sorted(os.listdir(directory_path))
    if not entries:
        return "directory is empty"

    preview = ", ".join(entries[:10])
    if len(entries) > 10:
        preview += f", ... ({len(entries)} entries total)"
    return preview


def build_test_artifacts_directory(project_directory, build_root, test_directory):
    """Build path to test artifacts directory."""
    return os.path.join(project_directory, build_root, "artifacts", test_directory)


def resolve_test_output_paths(project_directory, build_root, test_directory, output_directory, junit_filename, html_filename):
    """Resolve paths for test reports."""
    artifacts_directory = build_test_artifacts_directory(project_directory, build_root, test_directory)

    junit_source = os.path.join(artifacts_directory, junit_filename)
    html_source = os.path.join(artifacts_directory, html_filename)

    if not output_directory:
        raise ValueError("Output directory is not configured")
    
    resolved_output = resolve_path(project_directory, output_directory)
    target_directory = os.path.join(resolved_output, "ceedling-test-reports")
    junit_target = os.path.join(target_directory, junit_filename)
    html_target = os.path.join(target_directory, html_filename)
    
    return artifacts_directory, junit_source, html_source, target_directory, junit_target, html_target


def format_missing_test_report_error(report_label, expected_path, artifacts_directory, completed):
    """Format error message for missing test report."""
    command_output = ((completed.stdout or "") + (completed.stderr or "")).strip()
    artifact_summary = summarize_directory(artifacts_directory)
    message = (
        f"{report_label} was not generated at the expected path: {expected_path}. "
        f"Checked artifacts directory: {artifacts_directory}. Contents: {artifact_summary}."
    )

    if command_output:
        message += f" Ceedling output: {command_output}"

    message += (
        " If project.yml enables report_tests_log_factory with the expected report, "
        "this may indicate Ceedling wrote the report under a different filename or context."
    )
    return message


# ── Coverage utilities ────────────────────────────────────────────────────────

def build_coverage_artifacts_directory(project_directory, build_root):
    """Build path to coverage artifacts directory."""
    gcov_context = os.path.join("gcov", "gcovr")
    return os.path.join(project_directory, build_root, "artifacts", gcov_context)


def resolve_coverage_output_paths(project_directory, build_root, test_directory, output_directory, html_filename):
    """Resolve paths for coverage reports."""
    artifacts_directory = build_coverage_artifacts_directory(project_directory, build_root)
    html_source = os.path.join(artifacts_directory, html_filename)

    if not output_directory:
        raise ValueError("Output directory is not configured")
    
    resolved_output = resolve_path(project_directory, output_directory)
    target_directory = os.path.join(resolved_output, "ceedling-coverage-reports")
    html_target = os.path.join(target_directory, html_filename)
    
    return artifacts_directory, html_source, target_directory, html_target


def format_missing_coverage_report_error(expected_path, artifacts_directory, completed):
    """Format error message for missing coverage report."""
    command_output = ((completed.stdout or "") + (completed.stderr or "")).strip()
    artifact_summary = summarize_directory(artifacts_directory)
    message = (
        f"Coverage HTML report was not generated at the expected path: {expected_path}. "
        f"Checked artifacts directory: {artifacts_directory}. Contents: {artifact_summary}."
    )

    if command_output:
        message += f" Ceedling output: {command_output}"

    message += (
        " This tool expects the default gcovr HTML artifact name and output location produced by the init tool."
    )
    return message
