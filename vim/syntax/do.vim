" Vim syntax file
" Language: DO
" Maintainer: DO Team

if exists("b:current_syntax")
  finish
endif

syn keyword doKeyword fn let if else return
syn keyword doFunction main nextgroup=doFunctionCall
syn match doNumber '\d\+'
syn match doOperator '[+\-*/<>=!]'
syn match doFunction '\w\+\ze('
syn region doComment start="//" end="$"

hi def link doKeyword Keyword
hi def link doFunction Function
hi def link doNumber Number
hi def link doOperator Operator
hi def link doComment Comment

let b:current_syntax = "do"
