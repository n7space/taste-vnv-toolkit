.PHONY: all test clean build run-gui format

CURRENT_DIRECTORY=$(shell pwd)
PROJECT_DIRECTORY=src/taste-vnv-toolkit
PROJECT_FILE_PATH=${PROJECT_DIRECTORY}/taste-vnv-toolkit.csproj
DEFAULT_CONFIG_FILE=tvnvtk_config.xml

all: build

clean:
	rm -r -f output/*
	dotnet clean ${PROJECT_FILE_PATH}

format:
	dotnet format ${PROJECT_FILE_PATH}

build:
	dotnet build ${PROJECT_FILE_PATH}

test:
	dotnet test ${PROJECT_FILE_PATH}
	
run-gui:
	cd ${PROJECT_DIRECTORY} && \
	(dotnet run gui -c ${DEFAULT_CONFIG_FILE} || true) && \
	cd ${CURRENT_DIRECTORY}