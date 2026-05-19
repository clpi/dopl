CC ?= cc
CFLAGS ?= -O2
LDFLAGS ?=

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin

SRCS = main.c lexer.c parser.c codegen.c
OBJS = $(SRCS:.c=.o)

TEST_SRCS = test_main.c lexer.c parser.c codegen.c

.PHONY: all clean test install uninstall

all: doc

doc: $(SRCS)
	$(CC) $(CFLAGS) -o $@ $(SRCS) $(LDFLAGS)

test_main: $(TEST_SRCS)
	$(CC) $(CFLAGS) -o $@ $(TEST_SRCS) $(LDFLAGS)

test: doc test_main
	./test.sh

install: doc
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 doc $(DESTDIR)$(BINDIR)/ado

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/ado

clean:
	rm -f doc test_main
