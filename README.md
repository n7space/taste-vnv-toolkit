# TASTE V&V Toolkit

## General

TASTE V&V Toolkit (TVnVTK), created as a part of "Model-Based Execution Platform for Space Applications" project (contract 4000146882/24/NL/KK) financed by the European Space Agency.

The toolkit is intended to be used within TASTE toolchain environment, launched from SpaceCreator (GUI) or CI (CLI), such as Jenkins, GitLab or GitHub.

The toolkit loads a set of tools from the directory defined in its options, and launches them with relevant parameters. Each tool is defined via an XML with metadata (tool name, group, settings, script names...) and 3 python scripts:
- to check tool status,
- to view tool results,
- to execute the tool.

Tools can be defined and modified by the users to suit their needs and toolchains. 


## Built-in tools

### Clang-Format

Executes code style validation according to project specfic settings.

Prerequisites:
    * clang-format 

### Clang-Tidy naming check

Executes code naming style validation according to project specfic settings.

Prerequisites:
    * clang-tidy 
