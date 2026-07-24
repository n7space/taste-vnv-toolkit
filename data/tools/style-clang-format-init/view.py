from clangshared import check_clang_format_file_exists, get_clang_format_file_path

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    file_path = get_clang_format_file_path(taste_project_directory)
    exists, error_message = check_clang_format_file_exists(file_path)

    if not exists:
        status = "error"
        status_text = f"{error_message}\nRun the tool first to initialize it."
        show_status = True
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            status = "ok"
            status_text = content
            show_status = True
        except Exception as exc:
            status = "error"
            status_text = f"Failed to read .clang-format: {exc}"
            show_status = True
