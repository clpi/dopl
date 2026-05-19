CC=gcc
CFLAGS=-O2 -Wall -Wextra

all: doc test_lexer

doc: main.c lexer.c parser.c codegen.c
	$(CC) $(CFLAGS) -o $@ $^

test_lexer: test_lexer.c lexer.c
	$(CC) $(CFLAGS) -o $@ $^

test: doc test_lexer
	./test_lexer
	./test.sh

clean:
	rm -f doc test_lexer
