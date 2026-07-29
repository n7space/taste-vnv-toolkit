import subprocess

from clangshared import get_clang_tidy_command, get_clang_style_file_path
from vnvtoolkit import get_setting


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)

__DEFAULT_STYLE = """
Checks: '-*,readability-identifier-naming'

CheckOptions:
  - key: readability-identifier-naming.ClassCase
    value: CamelCase

  - key: readability-identifier-naming.FunctionCase
    value: lower_case

  - key: readability-identifier-naming.FunctionIgnoredRegexp
    value: ^[a-z_][a-z0-9_]*_(startup|(PI|RI)_[A-Za-z_][A-Za-z0-9_]*)$

  - key: readability-identifier-naming.VariableCase
    value: camelBack

  - key: readability-identifier-naming.PrivateMemberPrefix
    value: m_

  - key: readability-identifier-naming.EnumCase
    value: CamelCase

  - key: readability-identifier-naming.EnumConstantCase
    value: Camel_Snake_Case

  - key: readability-identifier-naming.ConstantCase
    value: UPPER_CASE

  - key: readability-identifier-naming.MacroDefinitionCase
    value: UPPER_CASE

  - key: readability-identifier-naming.AbstractClassCase
    value: CamelCase

  - key: readability-identifier-naming.StructCase
    value: CamelCase

  - key: readability-identifier-naming.UnionCase
    value: CamelCase

  - key: readability-identifier-naming.TypedefCase
    value: CamelCase

  - key: readability-identifier-naming.TypeAliasCase
    value: CamelCase

  - key: readability-identifier-naming.ConceptCase
    value: CamelCase

  - key: readability-identifier-naming.ScopedEnumConstantCase
    value: Camel_Snake_Case

  - key: readability-identifier-naming.GlobalFunctionCase
    value: lower_case

  - key: readability-identifier-naming.GlobalFunctionIgnoredRegexp
    value: ^[a-z_][a-z0-9_]*_(startup|(PI|RI)_[A-Za-z_][A-Za-z0-9_]*)$

  - key: readability-identifier-naming.ConstexprFunctionCase
    value: lower_case

  - key: readability-identifier-naming.MethodCase
    value: lower_case

  - key: readability-identifier-naming.ConstexprMethodCase
    value: lower_case

  - key: readability-identifier-naming.ClassMethodCase
    value: lower_case

  - key: readability-identifier-naming.PrivateMethodCase
    value: lower_case

  - key: readability-identifier-naming.ProtectedMethodCase
    value: lower_case

  - key: readability-identifier-naming.PublicMethodCase
    value: lower_case

  - key: readability-identifier-naming.VirtualMethodCase
    value: lower_case

  - key: readability-identifier-naming.NamespaceCase
    value: lower_case

  - key: readability-identifier-naming.InlineNamespaceCase
    value: lower_case

  - key: readability-identifier-naming.TemplateParameterCase
    value: CamelCase

  - key: readability-identifier-naming.TypeTemplateParameterCase
    value: CamelCase

  - key: readability-identifier-naming.TemplateTemplateParameterCase
    value: CamelCase

  - key: readability-identifier-naming.ValueTemplateParameterCase
    value: UPPER_CASE

  - key: readability-identifier-naming.ParameterPackCase
    value: lower_case

  - key: readability-identifier-naming.LocalVariableCase
    value: lower_case

  - key: readability-identifier-naming.GlobalVariableCase
    value: lower_case

  - key: readability-identifier-naming.StaticVariableCase
    value: lower_case

  - key: readability-identifier-naming.GlobalPointerCase
    value: lower_case

  - key: readability-identifier-naming.LocalPointerCase
    value: lower_case

  - key: readability-identifier-naming.MemberCase
    value: camelBack

  - key: readability-identifier-naming.ClassMemberCase
    value: camelBack

  - key: readability-identifier-naming.PublicMemberCase
    value: camelBack

  - key: readability-identifier-naming.ProtectedMemberCase
    value: camelBack

  - key: readability-identifier-naming.PrivateMemberCase
    value: camelBack

  - key: readability-identifier-naming.GlobalConstantCase
    value: UPPER_CASE

  - key: readability-identifier-naming.LocalConstantCase
    value: UPPER_CASE

  - key: readability-identifier-naming.StaticConstantCase
    value: UPPER_CASE

  - key: readability-identifier-naming.ClassConstantCase
    value: UPPER_CASE

  - key: readability-identifier-naming.ConstantMemberCase
    value: UPPER_CASE

  - key: readability-identifier-naming.ConstexprVariableCase
    value: UPPER_CASE

  - key: readability-identifier-naming.GlobalConstexprVariableCase
    value: UPPER_CASE

  - key: readability-identifier-naming.LocalConstexprVariableCase
    value: UPPER_CASE

  - key: readability-identifier-naming.StaticConstexprVariableCase
    value: UPPER_CASE

  - key: readability-identifier-naming.ClassConstexprCase
    value: UPPER_CASE

  - key: readability-identifier-naming.GlobalConstantPointerCase
    value: UPPER_CASE

  - key: readability-identifier-naming.LocalConstantPointerCase
    value: UPPER_CASE

  - key: readability-identifier-naming.ParameterCase
    value: lower_case

  - key: readability-identifier-naming.ParameterIgnoredRegexp
    value: ^(IN|OUT)_[a-zA-Z0=9_]+$

  - key: readability-identifier-naming.PointerParameterCase
    value: lower_case

  - key: readability-identifier-naming.PointerParameterIgnoredRegexp
    value: ^(IN|OUT)_[a-zA-Z0=9_]+$

  - key: readability-identifier-naming.ConstantParameterCase
    value: lower_case

  - key: readability-identifier-naming.ConstantPointerParameterCase
    value: lower_case

"""


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    try:
        emit_progress(10)

        file_path = get_clang_style_file_path(taste_project_directory)

        emit_progress(80)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(__DEFAULT_STYLE)

        emit_progress(100)

        status = "ok"
        status_text = f"Created .clang-tidy.style at: {file_path}"
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Failed to create .clang-tidy.style: {exc}"
        show_status = True
