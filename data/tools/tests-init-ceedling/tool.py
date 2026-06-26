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

	implem_directory = os.path.join(function_root, "implem", "default")
	if os.path.isdir(implem_directory):
		source_directories.append(implem_directory)
		include_directories.append(implem_directory)

	for child_name in sorted(os.listdir(function_root)):
		child_path = os.path.join(function_root, child_name)
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


def write_project_configuration(project_yml_path, project_directory, tests_folder, source_directories, include_directories):
	source_lines = [
		f"    - +:{to_project_relative(project_directory, source_directory)}/**"
		for source_directory in source_directories
	]
	include_lines = [
		f"    - {to_project_relative(project_directory, include_directory)}"
		for include_directory in include_directories
	]
	tests_path = tests_folder.replace(os.sep, "/")

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
		"",
		":defines:",
		"  :test:",
		"    - UNIT_TEST",
		"",
		":cmock:",
		"  :mock_prefix: mock_",
		"  :when_no_prototypes: :warn",
		"",
		":gcov:",
		"  :reports:",
		"    - HtmlBasic",
		"",
		":plugins:",
		"  :enabled:",
		"    - gcov",
		"",
	])

	with open(project_yml_path, "w", encoding="utf-8") as handle:
		handle.write(project_yml)


def ensure_test_stub(tests_root, function_name):
	function_test_directory = os.path.join(tests_root, function_name)
	os.makedirs(function_test_directory, exist_ok=True)

	test_file_path = os.path.join(function_test_directory, f"test_{function_name}.c")
	if os.path.exists(test_file_path):
		return

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
		write_project_configuration(
			project_yml_path,
			taste_project_directory,
			tests_folder,
			source_directories,
			include_directories,
		)

		emit_progress(75)

		for function_name in function_names:
			ensure_test_stub(tests_root, function_name)

		emit_progress(100)

		status = "ok"
		status_text = f"Initialized Ceedling tests in {tests_root} for {len(function_names)} functions"
		show_status = True

	except FileNotFoundError as exc:
		status = "error"
		status_text = str(exc)
		show_status = True

	except Exception as exc:
		status = "error"
		status_text = f"Unexpected error: {exc}"
		show_status = True
