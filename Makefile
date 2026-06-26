SOLUTION_FILE_PATH=src/taste-vnv-toolkit.slnx
TEST_PROJECT_FILE_PATH=src/taste-vnv-toolkit-tests/taste-vnv-toolkit-tests.csproj
CURRENT_DIRECTORY=$(shell pwd)
PROJECT_DIRECTORY=src/taste-vnv-toolkit
PROJECT_FILE_PATH=${PROJECT_DIRECTORY}/taste-vnv-toolkit.csproj
DEFAULT_CONFIG_FILE=tvnvtk_config.xml

.PHONY: all test clean build build-release build-debug run-gui format

all: build

clean:
	rm -r -f output/*
	dotnet clean --no-restore ${SOLUTION_FILE_PATH}

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