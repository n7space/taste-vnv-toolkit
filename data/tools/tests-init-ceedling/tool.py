import os
import re
import xml.etree.ElementTree as ET


def emit_progress(value):
	if "report_progress" in globals():
		report_progress(value)


def normalize_function_name(function_name):
	return re.sub(r"\s+", "_", function_name.strip().lower())


def deduplicate(items):
	seen = set()
	unique_items = []
	for item in items:
		if item in seen:
			continue
		seen.add(item)
		unique_items.append(item)
	return unique_items


def to_project_relative(base_directory, target_directory):
	relative_path = os.path.relpath(target_directory, base_directory)
	return relative_path.replace(os.sep, "/")


def collect_language_paths(root_directory):
	source_directories = []
	include_directories = []

	for child_name in sorted(os.listdir(root_directory)):
		child_path = os.path.join(root_directory, child_name)
		if not os.path.isdir(child_path):
			continue

		src_directory = os.path.join(child_path, "src")
		wrappers_directory = os.path.join(child_path, "wrappers")

		if os.path.isdir(src_directory):
			source_directories.append(src_directory)
			include_directories.append(src_directory)

		if os.path.isdir(wrappers_directory):
			source_directories.append(wrappers_directory)
			include_directories.append(wrappers_directory)

	return deduplicate(source_directories), deduplicate(include_directories)


def collect_source_files(source_directories):
	source_files = []

	for source_directory in source_directories:
		for child_name in sorted(os.listdir(source_directory)):
			child_path = os.path.join(source_directory, child_name)
			if os.path.isfile(child_path) and child_name.endswith(".c"):
				source_files.append(child_path)

	return deduplicate(source_files)


def collect_support_files(source_directories):
	"""Collect source files for :support section - implementation files and dataview files only, no wrappers."""
	support_files = []

	for source_directory in source_directories:
		# Skip wrapper directories
		if source_directory.endswith("wrappers") or "/wrappers/" in source_directory.replace(os.sep, "/"):
			continue

		for child_name in sorted(os.listdir(source_directory)):
			child_path = os.path.join(source_directory, child_name)
			if os.path.isfile(child_path) and child_name.endswith(".c"):
				support_files.append(child_path)

	return deduplicate(support_files)


def get_tests_root():
	tests_folder = "test"
	for setting_name, setting_value in settings:
		if setting_name == "Tests folder":
			tests_folder = str(setting_value)
	return tests_folder


def get_top_level_function_names(interfaceview_path):
	tree = ET.parse(interfaceview_path)
	root = tree.getroot()

	function_names = []
	for function_element in root.findall("./Function"):
		function_name = function_element.get("name", "")
		normalized_name = normalize_function_name(function_name)
		if normalized_name:
			function_names.append(normalized_name)

	return deduplicate(function_names)


def collect_function_paths(project_directory, function_name):
	function_root = os.path.join(project_directory, "work", function_name)
	if not os.path.isdir(function_root):
		raise FileNotFoundError(f"Generated work directory not found for function '{function_name}': {function_root}")

	source_directories = []
	include_directories = []
	implementation_languages = set()

	implem_directory = os.path.join(function_root, "implem", "default")
	if os.path.isdir(implem_directory):
		implem_sources, implem_includes = collect_language_paths(implem_directory)
		source_directories.extend(implem_sources)
		include_directories.extend(implem_includes)

		for child_name in sorted(os.listdir(implem_directory)):
			child_path = os.path.join(implem_directory, child_name)
			if os.path.isdir(child_path):
				implementation_languages.add(child_name)

	for child_name in sorted(os.listdir(function_root)):
		if child_name == "implem" or child_name in implementation_languages:
			continue

		child_path = os.path.join(function_root, child_name)
		if not os.path.isdir(child_path):
			continue

		child_sources, child_includes = collect_language_paths(function_root)
		source_directories.extend(child_sources)
		include_directories.extend(child_includes)
		break

	return deduplicate(source_directories), deduplicate(include_directories)


def write_project_configuration(project_yml_path, project_directory, tests_folder, source_directories, include_directories):
	source_lines = [
		f"    - +:{to_project_relative(project_directory, source_directory)}/**"
		for source_directory in source_directories
	]
	support_file_lines = [
		f"    - {to_project_relative(project_directory, support_file)}"
		for support_file in collect_support_files(source_directories)
	]
	include_lines = [
		f"    - {to_project_relative(project_directory, include_directory)}"
		for include_directory in include_directories
	]
	tests_path = tests_folder.replace(os.sep, "/")

	# Build :files: section only if there are support files
	files_section = []
	if support_file_lines:
		files_section = [
			"",
			":files:",
			"  :support:",
			*support_file_lines,
		]

	project_yml = "\n".join([
		":project:",
		"  :which_ceedling: gem",
		"  :build_root: build",
		"  :use_test_preprocessor: :all",
		"  :use_mocks: TRUE",
		"",
		":paths:",
		"  :test:",
		f"    - +:{tests_path}/**",
		"  :source:",
		*source_lines,
		"  :include:",
		*include_lines,
		*files_section,
		"",
		":defines:",
		"  :test:",
		"    - UNIT_TEST",
		"",
		":cmock:",
		"  :mock_prefix: mock_",
		"  :when_no_prototypes: :warn",
		"",
		":report_tests_log_factory:",
		"  :reports:",
		"    - junit",
		"    - html",
		"",
		":gcov:",
		"  :reports:",
		"    - HtmlDetailed",
		"  :utilities:",
		"    - gcovr",
		"  :gcovr:",
		"    :report_exclude: \"work/dataview\"",
		"",
		":plugins:",
		"  :enabled:",
		"    - report_tests_log_factory",
		"    - gcov",
		"",
	])

	project_state = "created"
	if os.path.exists(project_yml_path):
		with open(project_yml_path, "r", encoding="utf-8") as handle:
			existing_project_yml = handle.read()
		if existing_project_yml == project_yml:
			return "unchanged"
		project_state = "updated"

	with open(project_yml_path, "w", encoding="utf-8") as handle:
		handle.write(project_yml)

	return project_state


def ensure_test_stub(tests_root, function_name):
	function_test_directory = os.path.join(tests_root, function_name)
	if os.path.exists(function_test_directory):
		return False

	os.makedirs(function_test_directory, exist_ok=True)

	test_file_path = os.path.join(function_test_directory, f"test_{function_name}.c")
	test_stub = "\n".join([
		'#include "unity.h"',
		"",
		"void setUp(void)",
		"{",
		"}",
		"",
		"void tearDown(void)",
		"{",
		"}",
		"",
		f"void test_{function_name}_stubs(void)",
		"{",
		'    TEST_IGNORE_MESSAGE("Test not implemented");',
		"}",
		"",
	])

	with open(test_file_path, "w", encoding="utf-8") as handle:
		handle.write(test_stub)

	return True


tests_folder = get_tests_root()

if not tests_folder:
	status = "error"
	status_text = "Test folder is not configured"
	show_status = True
elif not taste_project_directory:
	status = "error"
	status_text = "Project directory is not configured"
	show_status = True
else:
	interfaceview_path = os.path.join(taste_project_directory, "interfaceview.xml")
	tests_root = os.path.abspath(os.path.join(taste_project_directory, tests_folder))

	try:
		emit_progress(5)

		if not os.path.isfile(interfaceview_path):
			raise FileNotFoundError(f"interfaceview.xml not found: {interfaceview_path}")

		function_names = get_top_level_function_names(interfaceview_path)
		if not function_names:
			raise ValueError("No top-level functions found in interfaceview.xml")

		emit_progress(20)

		source_directories = []
		include_directories = []
		for function_name in function_names:
			function_sources, function_includes = collect_function_paths(
				taste_project_directory, function_name
			)
			source_directories.extend(function_sources)
			include_directories.extend(function_includes)

		dataview_directory = os.path.join(taste_project_directory, "work", "dataview", "C")
		if not os.path.isdir(dataview_directory):
			raise FileNotFoundError(f"Generated dataview directory not found: {dataview_directory}")

		source_directories.append(dataview_directory)
		include_directories.append(dataview_directory)

		source_directories = deduplicate(source_directories)
		include_directories = deduplicate(include_directories)

		emit_progress(45)

		os.makedirs(tests_root, exist_ok=True)
		project_yml_path = os.path.join(taste_project_directory, "project.yml")
		project_state = write_project_configuration(
			project_yml_path,
			taste_project_directory,
			tests_folder,
			source_directories,
			include_directories,
		)

		emit_progress(75)

		created_count = 0
		for function_name in function_names:
			if ensure_test_stub(tests_root, function_name):
				created_count += 1

		emit_progress(100)

		status = "ok"
		project_message = {
			"created": "created project.yml",
			"updated": "updated project.yml",
			"unchanged": "kept project.yml unchanged",
		}[project_state]
		status_text = (
			f"Initialized Ceedling tests in {tests_root}: {project_message}; "
			f"created {created_count} function folders, skipped {len(function_names) - created_count} existing folders"
		)
		show_status = True

	except FileNotFoundError as exc:
		status = "error"
		status_text = str(exc)
		show_status = True

	except Exception as exc:
		status = "error"
		status_text = f"Unexpected error: {exc}"
		show_status = True
