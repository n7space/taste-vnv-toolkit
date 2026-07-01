VISUAL?=kate

all: compile-linux

clean:
	rm -rf obj

edit:
	$(VISUAL) ../../dataview/C/dataview-uniq.h \
                  src/datapool.h \
                  src/datapool.c

compile-linux:
	mkdir -p obj && cd obj && gcc -c ../src/*.c
