SOLUTION_FILE_PATH=src/taste-vnv-toolkit.slnx
TEST_PROJECT_FILE_PATH=src/taste-vnv-toolkit-tests/taste-vnv-toolkit-tests.csproj
CURRENT_DIRECTORY=$(shell pwd)
PROJECT_DIRECTORY=src/taste-vnv-toolkit
PROJECT_FILE_PATH=${PROJECT_DIRECTORY}/taste-vnv-toolkit.csproj
DEFAULT_CONFIG_FILE=tvnvtk_config.xml
DEMO_PROJECT_DIR=demo/demo-taste-project
ABSOLUTE_DEMO_PROJECT_DIR=$(abspath ${DEMO_PROJECT_DIR})

.PHONY: all test clean build build-release build-debug run-gui format demo-regenerate-trace

all: build

clean:
	rm -r -f output/*
	dotnet clean ${SOLUTION_FILE_PATH}

format:
	dotnet format --no-restore ${SOLUTION_FILE_PATH}

build: build-release

build-debug:
	dotnet build ${SOLUTION_FILE_PATH} --configuration Debug

build-release:
	dotnet build ${SOLUTION_FILE_PATH} --configuration Release

test:
	dotnet test --no-restore ${TEST_PROJECT_FILE_PATH} -l:"console;verbosity=normal"
	
run-gui:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore gui -c ${DEFAULT_CONFIG_FILE} || true) && \
	cd ${CURRENT_DIRECTORY}

demo-run:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- gui -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} || true) && \
	cd ${CURRENT_DIRECTORY}

demo-clean:
	rm -r -f ${DEMO_PROJECT_DIR}/test
	rm -r -f ${DEMO_PROJECT_DIR}/build
	rm -f ${DEMO_PROJECT_DIR}/project.yml

demo-test-init:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Initialize unit tests [ceedling]" || true) && \
	cd ${CURRENT_DIRECTORY}

demo-test:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Execute unit tests [ceedling]" || true) && \
	cd ${CURRENT_DIRECTORY}

demo-test-coverage:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Gather unit test coverage [ceedling]" || true) && \
	cd ${CURRENT_DIRECTORY}

demo-doxy-init:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Initialize Doxygen configuration" || true) && \
	cd ${CURRENT_DIRECTORY}

demo-doxy-run:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Generate Doxygen documentation" || true) && \
	cd ${CURRENT_DIRECTORY}

demo-doxy-xls:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Extract requirements from Excel to Doxygen tag file" || true) && \
	cd ${CURRENT_DIRECTORY}

demo-stack:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Check TASTE stack usage" || true) && \
	cd ${CURRENT_DIRECTORY}

demo-regenerate-trace:
	python3 demo/scripts/generate_trace.py demo/demo-taste-project/dummy-trace.miab

demo-perf-analyze-trace:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Performance Trace Analysis" || true) && \
	cd ${CURRENT_DIRECTORY}

demo-perf-get-trace:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run --no-restore -- run -c ${DEFAULT_CONFIG_FILE} -p ${ABSOLUTE_DEMO_PROJECT_DIR} "Get Performance Trace" || true) && \
	cd ${CURRENT_DIRECTORY}
