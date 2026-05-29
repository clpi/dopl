# Vim Syntax Highlighting for Ado

## Installation

### Manual Installation

Copy the syntax files to your Vim runtime directory:

```bash
mkdir -p ~/.vim/syntax ~/.vim/ftplugin
cp vim/syntax/ado.vim ~/.vim/syntax/
cp vim/ftplugin/ado.vim ~/.vim/ftplugin/
```

Add to your `.vimrc` or `init.vim`:

```vim
au BufRead,BufNewFile *.do set filetype=do
```

### For Neovim

```bash
mkdir -p ~/.config/nvim/syntax ~/.config/nvim/ftplugin
cp vim/syntax/ado.vim ~/.config/nvim/syntax/
cp vim/ftplugin/ado.vim ~/.config/nvim/ftplugin/
```

Add to your `init.lua`:

```lua
vim.filetype.add({
  extension = {
    do = 'ado',
  },
})
```

## Features

- Keyword highlighting: `fn`, `let`, `if`, `else`, `return`
- Function name highlighting
- Number highlighting
- Operator highlighting
- Comment support (with `//`)
- Auto-indentation (2 spaces)
