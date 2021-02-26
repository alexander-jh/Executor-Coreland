// --------------- lib_token.cpp ---------------
// Source file for lib_token.so dynamic C++ lib
//
// Compiler: G++
// STD:      C++11
// Author:   Alex Hoke
// Date:	 01/20/2021

#include "lib_token.hpp"

std::string resolve_token(const std::string& in) {
    std::string resolved;
    // Constant look-up for compiler tokens
    static const std::unordered_map<std::string, std::string> token_types {
            { "program", "PROGRAM" },
            { "begin", "BEGIN" },
            { "end", "END" },
            { "new", "NEW" },
            { "define", "DEFINE" },
            { "extends", "EXTENDS" },
            { "class", "CLASS" },
            { "endclass", "ENDCLASS" },
            { "int", "INT" },
            { "endfunc", "ENDFUNC" },
            { "if", "IF" },
            { "then", "THEN" },
            { "else", "ELSE" },
            { "while", "WHILE" },
            { "endwhile", "ENDWHILE" },
            { "endif", "ENDIF" },
            { ";", "SEMICOLON" },
            { "(", "LPAREN" },
            { ")", "RPAREN" },
            { ",", "COMMA" },
            { "=", "ASSIGN" },
            { "!", "NEGATION" },
            { "or", "OR" },
            { "==", "EQUAL" },
            { "<", "LESS" },
            { "<=", "LESSEQUAL" },
            { "+", "ADD" },
            { "-", "SUB" },
            { "*", "MULT" },
            { "input", "INPUT" },
            { "output", "OUTPUT" },
            { "const", "CONST" },
            { "id", "ID" },
            { "eof", "EOF" },
            { "error", "ERROR" }
    };
    // If input is a valid token return token, else return empty string
    auto token = token_types.find(in);
    (token != token_types.end()) ? (resolved = token->second) : (resolved = token_types.at("id"));
    return resolved;
}

std::pair<std::string, long> get_input(const char *f_name, long pos) {
    // Open file and set correct position
    std::ifstream in(f_name);
    in.seekg(pos);

    // Declare regex
    boost::regex valid_io(CHAR_PERMIT), end_input(TERMINAL_CHAR), spec_char(SPECIAL_CHAR);
    std::string input, next;

    // Reads until one of several conditions met
    // 1) EOF reached
    // 2) Terminal character read
    // 3) Breaks if invalid syntax found
    // 4) Two =, or <=
    next = (char) in.get();
    while(!regex_match(next, end_input) && !in.eof()) {
        if(!regex_match(next, valid_io)) {
            pos = in.tellg();
            in.close();
            return {"error", pos};
        }
        input += next;
        next = (char) in.get();
    }
    // Get current file pointer
    pos = in.tellg();
    // Rollback position if not at EOF and input is not empty to compensate for
    // the additional character consumed by larger tokens
    if(!in.eof() && !input.empty()) { --pos; } else if(input.empty() && regex_match(next, spec_char)) { input = next; }

    // Three major edge cases for housekeeping:
    // 1) File stream at EOF and there are no characters left to read in input or next
    // 2) CONST is greater than upper bound. is_number() uses an iterator, so if an all
    //    integer has a length greater than 4 it implies the number is outside of the domain
    // 3) Nothing has been written to input yet, but next is either = or <
    if(in.eof() && input.empty() && next.empty()) {
        input = "eof";
    } else if((is_number(input) && input.length() > 4) || (str_lol(input) > 1024)) {
        input = "error";
    } else if((input.empty() && next == "=") || (input.empty() && next == "<")) {
        input = next;
    // Check next character in buffer in case of == or <=. If second character is either
    // listed increment file pointer to new buffer stream location.
        char tmp = in.get();
        if(tmp == '=') {
            input += tmp;
            ++pos;
        }
    }
    // Close file stream, return {token, file pointer} pair
    in.close();
    return {input, pos};
}

bool inline is_number(const std::string& str) {
    // Iterator over the string, returns false on first non-digit. Doesn't make a sum
    // so no threat of overflow
    return !str.empty() && std::find_if(str.begin(), str.end(),[](unsigned char c)
    {return !std::isdigit(c);}) == str.end();
}

struct token_t next_token(const char *f_name, long pos) {
    // Declare temp sting, and token_t
    std::string name;
    token_t ret;
    // Reserve memory space so pair memory is not lost when first/second are passed to
    // token_t constructor
    auto token = new std::pair<std::string, long>;

    // Runs through white space to eof
    do {
        *token = get_input(f_name, pos);
        pos = token->second;
    } while(token->first.empty());

    // Classify token as CONST, ID, or other
    if(is_number(token->first)) {
        ret = token_t(resolve_token(std::string("const")), token->first, token->second);
    } else if((name = resolve_token(token->first)) == "ID") {
        ret = token_t(name, token->first, token->second);
    } else ret = token_t(name, NONE, token->second);

    // Return token_t struct and clear reserved memory
    delete token;
    return ret;
}

long str_lol(const std::string& str) {
    // Begin pointer of string set and terminates on nullptr which is equivalent to '\0'
    const char* begin = str.c_str();
    long value = std::strtol(begin, nullptr, RADIX);
    return value;
}
