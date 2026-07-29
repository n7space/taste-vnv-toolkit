from clangshared import get_clang_tidy_analysis_file_path
from vnvtoolkit import get_setting


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


def _get_bool(settings, name, default):
    val = get_setting(settings, name, default)
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("true", "1", "yes")


def _get_int(settings, name, default):
    try:
        return int(get_setting(settings, name, default))
    except (TypeError, ValueError):
        return default


def _build_checks(enable_quality, enable_security, enable_best_practice):
    """Assemble the Checks string from enabled themes."""
    checks = ["-*"]

    if enable_quality:
        checks += [
            # Function/method size and complexity analysis
            "readability-function-size",
            # Duplicate code detection (duplicated if/switch branches)
            "bugprone-branch-clone",
            # Dead code detection
            "clang-analyzer-deadcode.DeadStores",
            "misc-unused-parameters",
            # Loops with no visible exit condition
            "bugprone-infinite-loop",
            # Loop counter type too small for its range (embedded overflow pitfall)
            "bugprone-too-small-loop-variable",
            # Unstructured control flow, hurts complexity/maintainability
            "cppcoreguidelines-avoid-goto",
            # Unintended truncation from integer division
            "bugprone-integer-division",
        ]

    if enable_security:
        checks += [
            # Insecure C string / buffer API usage
            "clang-analyzer-security.insecureAPI.DeprecatedOrUnsafeBufferHandling",
            "clang-analyzer-security.insecureAPI.bcmp",
            "clang-analyzer-security.insecureAPI.bcopy",
            "clang-analyzer-security.insecureAPI.bzero",
            "clang-analyzer-security.insecureAPI.getpw",
            "clang-analyzer-security.insecureAPI.gets",
            "clang-analyzer-security.insecureAPI.mkstemp",
            "clang-analyzer-security.insecureAPI.mktemp",
            "clang-analyzer-security.insecureAPI.rand",
            "clang-analyzer-security.insecureAPI.strcpy",
            "clang-analyzer-security.insecureAPI.vfork",
            "cert-str34-c",
            "bugprone-suspicious-string-compare",
            "bugprone-not-null-terminated-result",
            # Buffer overflow / out-of-bounds access
            "clang-analyzer-security.ArrayBound",
            "cppcoreguidelines-pro-bounds-array-to-pointer-decay",
            "cppcoreguidelines-pro-bounds-constant-array-index",
            "cppcoreguidelines-pro-bounds-pointer-arithmetic",
            # Dangling pointer (returning / storing address of a local variable)
            "clang-analyzer-core.StackAddressEscape",
            # Dynamic memory issues: use-after-free, double-free, memory leaks
            "clang-analyzer-unix.Malloc",
            "clang-analyzer-unix.MismatchedDeallocator",
            # Unchecked return values of critical library calls
            "cert-err33-c",
            # Sign-extension bugs leading to negative array index / OOB access
            "bugprone-signed-char-misuse",
            # Non-reentrant function calls (race-condition risk in RTOS/multithreaded code)
            "concurrency-mt-unsafe",
        ]

    if enable_best_practice:
        checks += [
            # Prohibition of magic number usage
            "readability-magic-numbers",
            # Use of constant variables where expected
            "misc-const-correctness",
            "cppcoreguidelines-avoid-non-const-global-variables",
            # Require variables to be initialized before use
            "cppcoreguidelines-init-variables",
            "clang-analyzer-core.uninitialized.Assign",
            "clang-analyzer-core.uninitialized.Branch",
            "clang-analyzer-core.uninitialized.CapturedBlockVariable",
            "clang-analyzer-core.uninitialized.ArraySubscript",
            "clang-analyzer-core.uninitialized.UndefReturn",
            # Unsafe macro patterns (prefer constants / inline functions)
            "cppcoreguidelines-macro-usage",
            "bugprone-multiple-statement-macro",
            "bugprone-macro-parentheses",
            # Defensive programming: require default case in switch statements
            "bugprone-switch-missing-default-case",
            # Common memset/sizeof misuse patterns
            "bugprone-suspicious-memset-usage",
            "bugprone-sizeof-expression",
            # Avoid floating-point loop counters (precision pitfalls, CERT FLP30-C)
            "bugprone-float-loop-counter",
            # Avoid bitwise/memory comparison of floating-point values (CERT EXP42-C)
            "cert-exp42-c",
            # Avoid dynamic memory allocation (heap use prohibition, common in safety-critical
            # embedded software). Note: may produce false positives on ASN.1/PolyORB-generated
            # TASTE glue code that legitimately uses heap allocation. Use // NOLINT or disable
            # this theme if the noise is excessive for your project.
            "cppcoreguidelines-no-malloc",
        ]

    return ",".join(checks)


def _build_check_options(
    enable_quality,
    enable_best_practice,
    max_lines,
    max_statements,
    max_branches,
    max_params,
    max_nesting,
    magic_ignored,
):
    """Assemble the CheckOptions YAML block from enabled themes and thresholds."""
    options = []

    if enable_quality:
        options += [
            ("readability-function-size.LineThreshold", str(max_lines)),
            ("readability-function-size.StatementThreshold", str(max_statements)),
            ("readability-function-size.BranchThreshold", str(max_branches)),
            ("readability-function-size.ParameterThreshold", str(max_params)),
            ("readability-function-size.NestingThreshold", str(max_nesting)),
        ]

    if enable_best_practice:
        options += [
            ("readability-magic-numbers.IgnoredIntegerValues", magic_ignored),
            ("misc-const-correctness.WarnPointersAsValues", "false"),
            ("misc-const-correctness.TransformValues", "false"),
        ]

    if not options:
        return ""

    lines = ["CheckOptions:"]
    for key, value in options:
        lines.append(f"  - key: {key}")
        lines.append(f"    value: '{value}'")
    return "\n".join(lines) + "\n"


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    try:
        emit_progress(10)

        enable_quality = _get_bool(settings, "Enable code quality checks", True)
        enable_security = _get_bool(settings, "Enable code security checks", True)
        enable_best_practice = _get_bool(
            settings, "Enable code best practice checks", True
        )
        max_lines = _get_int(settings, "Function max lines", 80)
        max_statements = _get_int(settings, "Function max statements", 40)
        max_branches = _get_int(settings, "Function max branches", 10)
        max_params = _get_int(settings, "Function max parameters", 8)
        max_nesting = _get_int(settings, "Max nesting depth", 5)
        magic_ignored_raw = str(
            get_setting(settings, "Magic number ignored values", "0;1;2")
        )
        magic_ignored = ";".join(
            v.strip()
            for v in magic_ignored_raw.replace(",", ";").split(";")
            if v.strip()
        )

        checks_str = _build_checks(
            enable_quality, enable_security, enable_best_practice
        )
        check_options_str = _build_check_options(
            enable_quality,
            enable_best_practice,
            max_lines,
            max_statements,
            max_branches,
            max_params,
            max_nesting,
            magic_ignored,
        )

        config_lines = [f"Checks: '{checks_str}'\n"]
        if check_options_str:
            config_lines.append("\n" + check_options_str)

        emit_progress(70)

        file_path = get_clang_tidy_analysis_file_path(taste_project_directory)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(config_lines)

        emit_progress(100)

        status = "ok"
        status_text = f"Created .clang-tidy at: {file_path}"
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Failed to create .clang-tidy: {exc}"
        show_status = True
