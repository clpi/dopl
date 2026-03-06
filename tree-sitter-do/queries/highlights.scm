; Keywords
(function_declaration "fn" @keyword.function)
"let" @keyword
"if" @keyword.control
"else" @keyword.control
"return" @keyword.control

; Functions
(function_declaration name: (identifier) @function)
(call_expression function: (identifier) @function.call)

; Parameters
(parameter_list (identifier) @variable.parameter)

; Variables
(let_statement name: (identifier) @variable)

; Operators
["+" "-" "*" "/" "==" "!=" "<" ">" "<=" ">="] @operator
"=" @operator

; Literals
(number) @number

; Punctuation
["(" ")" "{" "}"] @punctuation.bracket
"," @punctuation.delimiter
