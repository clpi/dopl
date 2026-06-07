CC ?= cc
CFLAGS ?= -O2

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin

SRCS = main.c lexer.c parser.c codegen.c codegen_wasm.c
OBJS = $(SRCS:.c=.o)

TEST_SRCS = test_main.c lexer.c parser.c codegen.c codegen_wasm.c

.PHONY: all clean test bench install install-lsp uninstall wasm-test

all: doc

doc: $(SRCS)
	$(CC) $(CFLAGS) -o $@ $(SRCS) -lcurl

test_main: $(TEST_SRCS)
	$(CC) $(CFLAGS) -o $@ $(TEST_SRCS) -lcurl

test: doc test_main
	./test.sh

wasm: doc
	./doc --target wasm examples/stdlib.do
	wat2wasm examples/stdlib.do.wat -o examples/stdlib.do.wasm
	@echo "WASM module ready: examples/stdlib.do.wasm"

wasm-test: doc
	@echo "Building WASM test..."
	./doc --target wasm examples/stdlib.do
	wat2wasm examples/stdlib.do.wat -o examples/stdlib.do.wasm
	@echo "WASM module ready: examples/stdlib.do.wasm"

bench: doc
	./benchmarks/run.sh

install: doc install-lsp
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 doc $(DESTDIR)$(BINDIR)/ado

install-lsp:
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 lsp/ado_lsp.py $(DESTDIR)$(BINDIR)/ado-lsp

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/ado
	rm -f $(DESTDIR)$(BINDIR)/ado-lsp

clean:
	rm -f doc test_main
