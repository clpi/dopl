" Ado file type plugin
setlocal commentstring=#\ %s
setlocal formatoptions+=croql
setlocal tabstop=2 shiftwidth=2 expandtab
setlocal matchpairs+=(:)
setlocal suffixesadd=.do

" Auto-format on save (optional)
" autocmd BufWritePre <buffer> lua vim.lsp.buf.format()
