
This grammar uses EBNF notation, with a simple extension that reduces grammar size.
Productions can be parameterized. Parameters can be set to both non-terminals and terminals.
Parameterized productions behave as templates, which are instantiated whenever parameterized
non-terminal is used with actual parameter values.

In this grammar, symbols are lines of input bash script

```
file = { ignored-symbol } , [ header ] , { ignored-symbol | definition } ;

header = directive(module-symbol) , { header-attribute | spacing-symbol } ;

header-attribute = directive(author-symbol) ;    (* more header attributes here *)

directive(directive-symbol) = directive-symbol ;

definition = func-definition ;   (* more definitions here *)

func-definition = directive(func-symbol) , { func-attribute } ;

func-attribute = text ; (* TODO: arg status output *);


ignored-symbol  = ? any line not recognized as specific symbol ?;

spacing-symbol  = ? line matching '^# *$' ?     (* empty line in comment *)

module-symbol   = ? line matching '^# @module ' ?
author-symbol   = ? line matching '^# @author ' ?

func_symbol .......
```

