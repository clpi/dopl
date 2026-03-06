" Ado Language Syntax
if exists("b:current_syntax")
    finish
endif

syn keyword adoKeyword fn let if else while for return true false and or not
syn keyword adoBuiltin print len push
syn match adoNumber /\d\+/
syn match adoOperator /[-+*/%<>=!]=\|[<>]\|[-+*/]/
syn region adoString start=/"/ skip=/\\"/ end=/"/
syn region adoComment start=/#/ end=/$/
syn match adoFuncCall /\w\+\ze\s*(/
syn match adoIdentifier /\w\+/

hi def link adoKeyword Keyword
hi def link adoBuiltin Function
hi def link adoNumber Number
hi def link adoString String
hi def link adoComment Comment
hi def link adoOperator Operator
hi def link adoFuncCall Function
hi def link adoIdentifier Identifier

let b:current_syntax = "ado"
