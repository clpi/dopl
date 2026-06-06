CC ?= cc
CFLAGS ?= -O2
LDFLAGS ?=

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin

SRCS = main.c lexer.c parser.c codegen.c
OBJS = $(SRCS:.c=.o)

TEST_SRCS = test_main.c lexer.c parser.c codegen.c

.PHONY: all clean test bench install install-lsp uninstall

all: doc

doc: $(SRCS)
	$(CC) $(CFLAGS) -o $@ $(SRCS) $(LDFLAGS)

test_main: $(TEST_SRCS)
	$(CC) $(CFLAGS) -o $@ $(TEST_SRCS) $(LDFLAGS)

test: doc test_main
	./test.sh

bench: doc
	./benchmarks/run.sh

install: doc install-lsp

install-lsp:
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 lsp/do_lsp.py $(DESTDIR)$(BINDIR)/do-lsp

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/ado
	rm -f $(DESTDIR)$(BINDIR)/do-lsp

clean:
	rm -f doc test_main
