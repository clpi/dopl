-- Ado Language Neovim Configuration
local config_dir = vim.fn.expand('<sfile>:p:h')
local project_root = vim.fn.fnamemodify(config_dir, ':h')

-- Set up filetype detection
vim.filetype.add({
  extension = {
    do = 'ado',
  },
})

-- Load syntax highlighting
vim.cmd('set runtimepath+=' .. project_root .. '/vim')

-- Set up Tree-sitter if available
local has_treesitter, ts_configs = pcall(require, 'nvim-treesitter.parsers')
if has_treesitter then
  local parser_config = ts_configs.get_parser_configs()
  parser_config.ado = {
    install_info = {
      url = project_root .. '/tree-sitter-do',
      files = {'src/parser.c'},
      branch = 'main',
    },
    filetype = 'ado',
  }
  
  local has_ts_config, ts_setup = pcall(require, 'nvim-treesitter.configs')
  if has_ts_config then
    ts_setup.setup({
      ensure_installed = {},
      highlight = { enable = true, additional_vim_regex_highlighting = false },
      indent = { enable = true },
    })
  end
end

-- Find LSP: check PATH first, then fall back to repo path
local function find_lsp()
  local lsp_in_path = vim.fn.executable("do-lsp")
  if lsp_in_path == 1 then
    return "do-lsp"
  end
  return project_root .. "/lsp/do-lsp.py"
end

-- Set up LSP
vim.api.nvim_create_autocmd("FileType", {
  pattern = "ado",
  callback = function()
    local lsp_opts = {
      name = "ado-lsp",
      cmd = { find_lsp() },
      root_dir = project_root,
      capabilities = vim.lsp.protocol.make_client_capabilities(),
      on_attach = function(client, bufnr)
        local opts = { buffer = bufnr, noremap = true, silent = true }
        
        -- Navigation
        vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
        vim.keymap.set('n', 'gD', vim.lsp.buf.type_definition, opts)
        vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)
        vim.keymap.set('n', 'gi', vim.lsp.buf.implementation, opts)
        
        -- Hover
        vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
        vim.keymap.set('n', '<C-k>', vim.lsp.buf.signature_help, opts)
        
        -- Refactoring
        vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
        vim.keymap.set('n', '<leader>f', function() vim.lsp.buf.format({ async = true }) end, opts)
        
        -- Code actions
        vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, opts)
        vim.keymap.set('n', '<leader>cl', vim.lsp.codelens.run, opts)
        
        -- Diagnostics
        vim.keymap.set('n', '[d', vim.diagnostic.goto_prev, opts)
        vim.keymap.set('n', ']d', vim.diagnostic.goto_next, opts)
        vim.keymap.set('n', '<leader>q', vim.diagnostic.setloclist, opts)
        vim.keymap.set('n', '<leader>e', vim.diagnostic.open_float, opts)
        
        -- Symbols
        vim.keymap.set('n', '<leader>o', vim.lsp.buf.document_symbol, opts)
        vim.keymap.set('n', '<leader>s', vim.lsp.buf.workspace_symbol, opts)
        
        -- Enable code lenses
        if client.server_capabilities.codeLensProvider then
          vim.api.nvim_create_autocmd({ 'BufEnter', 'CursorHold', 'InsertLeave' }, {
            buffer = bufnr,
            callback = vim.lsp.codelens.refresh,
          })
          vim.lsp.codelens.refresh()
        end
        
        print('Ado LSP attached - full IDE features enabled')
      end,
    }
    
    -- Enable additional capabilities
    lsp_opts.capabilities.textDocument.completion.completionItem.snippetSupport = true
    lsp_opts.capabilities.textDocument.completion.completionItem.resolveSupport = {
      properties = { 'documentation', 'detail', 'additionalTextEdits' }
    }
    
    vim.lsp.start(lsp_opts)
  end,
})

-- Autocompletion with nvim-cmp if available
local has_cmp, cmp = pcall(require, 'cmp')
if has_cmp then
  cmp.setup({
    sources = {
      { name = 'nvim_lsp' },
      { name = 'buffer' },
      { name = 'path' },
    },
    mapping = cmp.mapping.preset.insert({
      ['<C-b>'] = cmp.mapping.scroll_docs(-4),
      ['<C-f>'] = cmp.mapping.scroll_docs(4),
      ['<C-Space>'] = cmp.mapping.complete(),
      ['<C-e>'] = cmp.mapping.abort(),
      ['<CR>'] = cmp.mapping.confirm({ select = true }),
      ['<Tab>'] = cmp.mapping(function(fallback)
        if cmp.visible() then cmp.select_next_item()
        else fallback() end
      end, { 'i', 's' }),
      ['<S-Tab>'] = cmp.mapping(function(fallback)
        if cmp.visible() then cmp.select_prev_item()
        else fallback() end
      end, { 'i', 's' }),
    }),
    snippet = {
      expand = function(args)
        vim.snippet.expand(args.body)
      end,
    },
  })
end

-- Basic editor settings
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 2
vim.opt.tabstop = 2
vim.opt.smartindent = true
vim.opt.termguicolors = true
vim.opt.signcolumn = 'yes'
vim.opt.updatetime = 250
vim.opt.timeoutlen = 300
vim.opt.completeopt = 'menu,menuone,noselect'

-- Status line
vim.opt.laststatus = 2
vim.opt.statusline = '%f %m %r%=%l:%c %p%% [%{&filetype}]'

-- Diagnostic signs
local signs = { Error = "󰅚 ", Warn = "󰀪 ", Hint = "󰌶 ", Info = " " }
for type, icon in pairs(signs) do
  local hl = "DiagnosticSign" .. type
  vim.fn.sign_define(hl, { text = icon, texthl = hl, numhl = hl })
end

-- Diagnostic config
vim.diagnostic.config({
  virtual_text = { prefix = '●' },
  signs = true,
  underline = true,
  update_in_insert = false,
  severity_sort = true,
  float = { source = 'always', border = 'rounded' },
})

-- Floating window borders
local border = { '╭', '─', '╮', '│', '╯', '─', '╰', '│' }
local orig_util_open_floating_preview = vim.lsp.util.open_floating_preview
function vim.lsp.util.open_floating_preview(contents, syntax, opts, ...)
  opts = opts or {}
  opts.border = opts.border or border
  return orig_util_open_floating_preview(contents, syntax, opts, ...)
end

print('Ado Language environment loaded - Type :help lsp for LSP commands')
