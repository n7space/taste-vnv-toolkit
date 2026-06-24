SOLUTION_FILE_PATH=src/taste-vnv-toolkit.slnx
TEST_PROJECT_FILE_PATH=src/taste-vnv-toolkit-tests/taste-vnv-toolkit-tests.csproj
CURRENT_DIRECTORY=$(shell pwd)
PROJECT_DIRECTORY=src/taste-vnv-toolkit
PROJECT_FILE_PATH=${PROJECT_DIRECTORY}/taste-vnv-toolkit.csproj
DEFAULT_CONFIG_FILE=tvnvtk_config.xml

.PHONY: all test clean build run-gui format

all: build

clean:
	rm -r -f output/*
	dotnet clean ${SOLUTION_FILE_PATH}

format:
	dotnet format ${SOLUTION_FILE_PATH}

build:
	dotnet build ${SOLUTION_FILE_PATH}

test:
	dotnet test ${TEST_PROJECT_FILE_PATH}
	
run-gui:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run gui -c ${DEFAULT_CONFIG_FILE} || true) && \
	cd ${CURRENT_DIRECTORY}