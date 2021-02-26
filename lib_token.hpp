// --------------- lib_token.hpp ---------------
// Header file for lib_token.so dynamic C++ lib
//
// Compiler: G++
// STD:      C++11
// Author:   Alex Hoke
// Date:	 01/20/2021

#include <string>
#include <iostream>
#include <fstream>
#include <unordered_map>
#include <boost/regex.hpp>
#include <utility>

// Regex macros and useful string constant
#define CHAR_PERMIT "^[a-z]|[A-z]|[0-9]|!|,|\\*|;|\\+|-|=|\\(|\\)|!|<|\\s"
#define TERMINAL_CHAR "^\\s|,|\\+|-|;|!|\\*|\\(|\\)|=|<"
#define SPECIAL_CHAR "^,|\\+|-|;|!|\\*|\\(|\\)"
#define NONE std::string("none")
#define RADIX (int) 10

// Struct for passing/bundling token data
//  @token      -   String containing the enumerated token constant
//  @name       -   Contains ID or CONST value, otherwise is set to "none"
//  @fp         -   Current file pointer
struct token_t {
    const char *token;
    const char *name;
    long        fp;

    // Constructor for conversion to Python C_Strings (const char*)
    token_t(const std::string& t, const std::string& n, long f) {
        token = t.c_str(), name = n.c_str(), fp = f;};

    // Default constructor
    token_t() {
        token = nullptr;
        name = nullptr;
        fp = 0;
    };
};

// Constant look-up for if string is token or ID
//  @in         -   Input string reference to search static hashmap for
//  @returns    -   String containing the current token if valid
std::string resolve_token(const std::string& in);

// Opens file and verifies current token
//  @f_name     -   String of the file location to read
//  @pos        -   Current integer position in the input file
//  @returns    -   Pair containing the read token and the current file pointer
std::pair<std::string, long> get_input(const char *f_name, long pos);

// Verifies if the given string is a pure number containing only 0-9. Runs inline
// since the unordered_map is statically declared to minimize r-value passing
//  @str        -   String to verify
//  @returns    -   Boolean telling if it is a number or not
bool inline is_number(const std::string& str);

// Link to extern C for Python Ctypes linkage
extern "C"

// Reads and validates the next token in the file stream
//  @f_name     -   String of the current file name to read
//  @pos        -   Current file pointer position
//  @returns    -   Struct tuple containing <token, name(if valid), file pointer>
struct token_t next_token(const char *f_name, long pos);

// Raw implementation of stoi to override compiler error using strtol
// @str         -   Const string passed by reference to covert
// @returns     -   Long integer representation of string
long str_lol(const std::string& str);