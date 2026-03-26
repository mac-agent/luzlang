/* luz_lexer.c
 * 
 * Luz lexer implemented in C.
 * Compiled as a shared library (.dll / .so) and loaded by the python brigde
 * 
 * Stage 1 - Infrastructure only:
 *   lexer_init, advance, current_char, peek_char,
 *   skip_whitespace, skip_comment, lex_all (stub), free_tokens.
 * 
 * Later stages will fill lex_all() with actual token production.
 */

#include "luz_lexer.h"

#include <stdio.h>   /* printf - used only in the test main() */
#include <stdlib.h>  /* malloc, realloc, free */
#include <string.h>  /* strlen, strdup, strcmp */
#include <ctype.h>   /* isdigit, isalpha, isspace */

/* ── Internal helpers ────────────────────────────────────────────────────────
 * These four functions are the only war the rest of the lexer touches the
 * source string.  Keeping all bounds-checking here means every caller can
 * assume safety without repeating the same pos < lenght guard.
 */

/* current_char() returns the character at the current position, or '\0' when
 * the lexer has consumed every character.  '\0' is used as the EOF sentinel
 * because it cannot appear in valid Luz source (Luz strings use \0 escape
 * only inside string literals, which the lexe handles specially).
 */
static char current_char(const CLexer* lex) {
    if (lex->pos < lex->length)
        return lex->source[lex->pos];
    return '\0';
}

/* peek_char() looks one step ahead without consuming anything.
 * Used by operators that need lookahead: '=' could be ASSIGN or EE,
 * '*' could be MUL or POW, etc.
 * Returns '\0' if we are at the last character or past the end.
*/
static char peek_char(const CLexer* lex) {
    if (lex->pos + 1 < lex->length)
        return lex->source[lex->pos + 1];
    return '\0';
}

/* advance() moves the position forward by one character and keeps line/col
 * in sync.  This is the single choke-point through which every consumed
 * character passes - the same design as the Python lexer.
 * 
 * When the current character is '\n':
 *   line is incremented and col is reset to 1 so that the NEXT character
 *   will be reported as column 1 of the new line.
 * For every other character:
 *   col is simply incremented.
 * 
 * Calling advance() when already at end-of-input is a no-op.
*/
static void advance(CLexer* lex) {
    if (lex->pos >= lex->length)
        return;
    if (lex->source[lex->pos] == '\n') {
        lex->line++;
        lex->col = 1;
    } else {
        lex->col++;
    }
    lex->pos++;
}

static void skip_whitespace(CLexer* lex) {
    while (current_char(lex) != '\0' && isspace((unsigned char)current_char(lex)))
        advance(lex);
}


static void skip_comment(CLexer* lex) {
    while (current_char(lex) != '\0' && current_char(lex) != '\n')
        advance(lex);
    advance(lex);   /* consume the '\n' */
}


static CToken make_token(TokenType type, int line, int col) {
    CToken t;
    t.type  = type;
    t.value = NULL;
    t.line  = line;
    t.col   = col;
    return t;
}


static CToken make_value_token(TokenType type, const char* value, int line, int col) {
    CToken t;
    t.type  = type;
    t.value = strdup(value);
    t.line  = line;
    t.col   = col;
    return t;
}



typedef struct {
    CToken* data;
    int     count;
    int     capacity;
} TokenArray;

static int tarray_init(TokenArray* arr) {
    arr->capacity = 64;
    arr->count    = 0;
    arr->data     = (CToken*)malloc(arr->capacity * sizeof(CToken));
    return arr->data != NULL;   /* 0 = allocation failed */
}


static int tarray_push(TokenArray* arr, CToken token) {
    if (arr->count == arr->capacity) {
        int new_cap   = arr->capacity * 2;
        CToken* grown = (CToken*)realloc(arr->data, new_cap * sizeof(CToken));
        if (grown == NULL) return 0; /* out of memory */
        arr->data     = grown;
        arr->capacity = new_cap;
    }
    arr->data[arr->count++] = token;
    return 1;
}


/*── Public API ──────────────────────────────────────────────────────────────*/

void lexer_init(CLexer* lex, const char* source) {
    lex->source = source;
    lex->pos    = 0;
    lex->line   = 1;
    lex->col    = 1;
    lex->length = (int)strlen(source);
}


void free_tokens(CToken* tokens, int count) {
    int i;
    for (i = 0; i < count; i++) {
        if (tokens[i].value != NULL)
            free(tokens[i].value);
    }
    free(tokens);
}

CToken* lex_all(CLexer* lex, int* out_count) {
    TokenArray arr;
    if (!tarray_init(&arr)) {
        *out_count = 0;
        return NULL;
    }

    while (current_char(lex) != '\0') {
        /* Skip Whitespace - produces no tokens */
        if (isspace((unsigned char)current_char(lex))) {
            skip_whitespace(lex);
            continue;
        }

        /* Skip line comments */
        if (current_char(lex) == '#') {
            skip_comment(lex);
            continue;
        }

        {
            char buf[2] = { current_char(lex), '\0' };
            int line = lex->line, col = lex->col;
            advance(lex);
            tarray_push(&arr, make_value_token(TT_ERROR, buf, line, col));
        }
    }

    tarray_push(&arr, make_token(TT_EOF, lex->line, lex->col));

    *out_count = arr.count;
    return arr.data;
}



/* ── Test main ───────────────────────────────────────────────────────────────
*/
#ifdef LUZ_TEST

static const char* token_type_name(TokenType t) {
    switch (t)
    {
        case TT_EOF: return "EOF";
        case TT_ERROR: return "ERROR";
        default:       return "UNKNOWN";
    }
}

int main(void) {
    {
        CLexer lex;
        lexer_init(&lex, "ab\ncd");

        printf("char='%c' line=%d col=%d  (expect line=1 col=1)\n",
                current_char(&lex), lex.line, lex.col);
        advance(&lex);

        printf("char='%c' line=%d col=%d  (expect line=1 col=2)\n",
                current_char(&lex), lex.line, lex.col);
        advance(&lex);

        advance(&lex);
        
        printf("char='%c' line=%d col=%d  (expect line=2 col=1)\n",
                current_char(&lex), lex.line, lex.col);
        advance(&lex);

        printf("char='%c' line=%d col=%d  (expect line=2 col=1)\n",
                current_char(&lex), lex.line, lex.col);
        advance(&lex);

        printf("at end: char='%c' (expect'\\0')\n", current_char(&lex));
    }

    printf("\n");

    {
        CLexer lex;
        int count, i;
        CToken* tokens;

        lexer_init(&lex, "   \n   \n   ");
        tokens = lex_all(&lex, &count);

        printf("Token count for whitespace-only: %d   (expect 1)\n", count);
        for (i = 0; i < count; i++) {
            printf("  [%d] type=%s line=%d col=%d\n",
                   i, token_type_name(tokens[i].type),
                   tokens[i].line, tokens[i].col);
        }
        free_tokens(tokens, count);
    }
    printf("\n");

    {
        CLexer lex;
        int count;
        CToken* tokens;

        lexer_init(&lex, "# this is a comment\n#another one\n");
        tokens = lex_all(&lex, &count);

        printf("Token count after two comments: %d  (expect 1)\n", count);
        free_tokens(tokens, count);
    }

    printf("\nStage 1 OK\n");
    return 0;
}

#endif /* LUZ_TEST */