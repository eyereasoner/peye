// Python syntax coloring for peye programs, shared by the playground and the
// documentation pages. A small tokenizer for coloring only: it never decides
// what a program means. colorize returns HTML with tok-* classes, styled by
// python-highlight.css.
const KEYWORDS = new Set(['from', 'import', 'as', 'def', 'return', 'lambda', 'for', 'in', 'if', 'else', 'elif',
  'while', 'with', 'not', 'and', 'or', 'is', 'None', 'True', 'False', 'pass', 'class', 'yield']);
// Stating clauses.
const STATEMENTS = new Set(['fact', 'implies', 'implied_by', 'query', 'contradiction', 'preds', 'vars', 'facts_from',
  'clause', 'step']);
// Native predicates, controls and arithmetic functions, from peye/builtins.py, peye/dsl.py and peye/arith.py.
const BUILTINS = new Set(['unify', 'not_unify', 'identical', 'not_identical', 'compare', 'is_', 'eq', 'ne',
  'is_var', 'is_nonvar', 'is_ground', 'is_atom', 'is_number', 'is_int', 'is_float', 'is_compound', 'functor',
  'arg', 'univ', 'atom_chars', 'atom_codes', 'atom_length', 'atom_concat', 'call', 'once', 'not_', 'findall',
  'struct', 'abs', 'min', 'max', 'round', 'int', 'float', 'pow', 'gcd', 'lcm', 'floor', 'ceil', 'trunc', 'sqrt',
  'isqrt', 'exp', 'log', 'log2', 'log10', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'sinh', 'cosh',
  'tanh', 'hypot', 'degrees', 'radians', 'fmod', 'copysign', 'pi', 'e', 'tau']);
const OPERATORS = '+-*/%<>=&|^~@!:.';

export function colorize(text) {
  let out = '';
  let i = 0;
  while (i < text.length) {
    const ch = text[i];
    if (ch === '#') {
      const end = lineEnd(text, i);
      out += span('comment', text.slice(i, end)); i = end;
    } else if (ch === "'" || ch === '"') {
      const end = quotedEnd(text, i);
      out += span('string', text.slice(i, end)); i = end;
    } else if (/[0-9]/.test(ch) || (ch === '.' && /[0-9]/.test(text[i + 1] ?? ''))) {
      const match = /^(0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+|[0-9_]*\.?[0-9_]+([eE][+-]?[0-9_]+)?|[0-9][0-9_]*\.?)/.exec(text.slice(i));
      out += span('number', match[0]); i += match[0].length;
    } else if (/[A-Za-z_À-￿]/.test(ch)) {
      const word = /^[A-Za-z0-9_À-￿]+/.exec(text.slice(i))[0];
      const called = /^\s*\(/.test(text.slice(i + word.length));
      const kind = KEYWORDS.has(word) || (STATEMENTS.has(word) && called) ? 'keyword'
        : BUILTINS.has(word) && called ? 'operator'
          : called ? 'predicate'
            : /^[A-Z_]/.test(word) ? 'variable' : null;
      out += kind ? span(kind, word) : escapeHtml(word); i += word.length;
    } else if (OPERATORS.includes(ch)) {
      let j = i;
      while (j < text.length && OPERATORS.includes(text[j])) j++;
      out += span('operator', text.slice(i, j)); i = j;
    } else if ('()[]{},;'.includes(ch)) {
      out += span('punctuation', ch); i++;
    } else {
      out += escapeHtml(ch); i++;
    }
  }
  return out;
}

function lineEnd(text, from) {
  const end = text.indexOf('\n', from);
  return end < 0 ? text.length : end;
}

function quotedEnd(text, from) {
  const quote = text[from];
  if (text.startsWith(quote.repeat(3), from)) {
    const close = text.indexOf(quote.repeat(3), from + 3);
    return close < 0 ? text.length : close + 3;
  }
  let i = from + 1;
  while (i < text.length) {
    if (text[i] === '\\') { i += 2; continue; }
    if (text[i] === quote) return i + 1;
    if (text[i] === '\n') return i;
    i++;
  }
  return i;
}

function span(kind, text) { return `<span class="tok-${kind}">${escapeHtml(text)}</span>`; }
export function escapeHtml(text) { return text.replace(/[&<>]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[ch])); }
