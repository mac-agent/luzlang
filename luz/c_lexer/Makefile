CC = gcc
CFLAGS = -Wall -Wextra -O2


ifeq ($(OS), Windows_NT)
	LIB = luz_lexer.dll
	LFLAGS = -shared
else
	LIB = luz_lexer.so
	LFLAGS = -shared -fPIC
endif

# Default target: shared library

$(LIB): luz_lexer.c luz_lexer.h
	  $(CC) $(CFLAGS) $(LFLAGS) luz_lexer.c -o $(LIB)
	  @echo "Built $(LIB)"
	

test: luz_lexer.c luz_lexer.h
	  $(CC) $(CFLAGS) -DLUZ_TEST luz_lexer.c -o lexer_test
	  ./lexer_test

clean:
	  rm -f $(LIB) lexer_test lexer_test.exe

.PHONY: test_clean