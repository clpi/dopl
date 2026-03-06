module.exports = grammar({
  name: 'do',

  rules: {
    source_file: $ => repeat($._statement),

    _statement: $ => choice(
      $.function_declaration,
      $.let_statement,
      $.if_statement,
      $.return_statement,
      $.expression_statement
    ),

    function_declaration: $ => seq(
      'fn',
      field('name', $.identifier),
      '(',
      optional($.parameter_list),
      ')',
      field('body', $.block)
    ),

    parameter_list: $ => sep1($.identifier, ','),

    block: $ => seq(
      '{',
      repeat($._statement),
      '}'
    ),

    let_statement: $ => seq(
      'let',
      field('name', $.identifier),
      '=',
      field('value', $._expression)
    ),

    if_statement: $ => seq(
      'if',
      field('condition', $._expression),
      field('consequence', $.block),
      optional(seq('else', field('alternative', $.block)))
    ),

    return_statement: $ => seq(
      'return',
      $._expression
    ),

    expression_statement: $ => $._expression,

    _expression: $ => choice(
      $.binary_expression,
      $.call_expression,
      $.identifier,
      $.number
    ),

    binary_expression: $ => choice(
      prec.left(1, seq($._expression, choice('+', '-'), $._expression)),
      prec.left(2, seq($._expression, choice('*', '/'), $._expression)),
      prec.left(0, seq($._expression, choice('==', '!=', '<', '>', '<=', '>='), $._expression))
    ),

    call_expression: $ => seq(
      field('function', $.identifier),
      '(',
      optional($.argument_list),
      ')'
    ),

    argument_list: $ => sep1($._expression, ','),

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,
    number: $ => /\d+/
  }
});

function sep1(rule, separator) {
  return seq(rule, repeat(seq(separator, rule)));
}
