from lark import Lark
from lark.lexer import Token
from lark.visitors import InlineTransformer

from mel_ast import *

parser = Lark('''
    %import common.NUMBER
    %import common.ESCAPED_STRING
    %import common.CNAME
    %import common.NEWLINE
    %import common.WS

    %ignore WS

    COMMENT: "/*" /(.|\\n|\\r)+/ "*/"
        |  "//" /(.)+/ NEWLINE
    %ignore COMMENT
    
    INT:        "int"
    CHAR:       "char"
    STRING:     "string"
    BOOLEAN:    "boolean"
    DOUBLE:     "double"
    VOID:       "void"
    
    TRUE:       "True"
    FALSE:      "False"
    ESCAPED_CHAR: "\'" /./ "\'"

    num: NUMBER  -> literal
    char: ESCAPED_CHAR  -> literal
    str: ESCAPED_STRING  -> literal
    bool: (TRUE|FALSE)  -> literal
    simple_type: INT | CHAR | STRING | BOOLEAN | DOUBLE
    array_type: simple_type "[" "]"
    type: simple_type | array_type
    ident: CNAME
    ?complex_ident: ident | ident"[" expr "]"

    ADD:     "+"
    SUB:     "-"
    MUL:     "*"
    DIV:     "/"
    MOD:     "%"
    AND:     "&&"
    OR:      "||"
    BIT_AND: "&"
    BIT_OR:  "|"
    GE:      ">="
    LE:      "<="
    NEQUALS: "!="
    EQUALS:  "=="
    GT:      ">"
    LT:      "<"

    call: ident "(" ( expr ( "," expr )* )? ")"
    
    type_list: (type ("," type)*)?
    
    
    ?group: num | char| str | bool
        | complex_ident
        | call
        | "(" expr ")"

    ?mult: group
        | mult ( MUL | DIV |  MOD) group  -> bin_op

    ?add: mult
        | add ( ADD | SUB ) mult  -> bin_op

    ?compare1: add
        | add ( GT | LT | GE | LE ) add  -> bin_op

    ?compare2: compare1
        | compare1 ( EQUALS | NEQUALS ) compare1  -> bin_op

    ?logical_and: compare2
        | logical_and AND compare2  -> bin_op

    ?logical_or: logical_and
        | logical_or OR logical_and  -> bin_op

    ?expr: logical_or

    ?vars_assign: ident
       | ident "As" simple_type "=" expr


    ?simple_stmt: ident "=" expr -> assign
        | call


    ?stmt: "Dim" vars_assign
        | "Dim" simple_stmt 
        | "if" "(" expr ")" "then" stmt_list ("else" stmt_list)? "end if" -> if
        | "for" simple_stmt "To" expr  stmt_list "Next" ident-> for
        | "while" "(" expr ")" ("AndAlso" "(" expr ")")? stmt "end while"-> while
        | "do" "while" "(" expr ")" stmt_list "Loop"-> do_while

    stmt_list: ( stmt )*
    
    
    ?prog: stmt_list

    ?start: prog
''', start='start')  # , parser='lalr')



class MelASTBuilder(InlineTransformer):
    def __getattr__(self, item):
        if isinstance(item, str) and item.upper() == item:
            return lambda x: x

        if item in ('bin_op',):
            def get_bin_op_node(*args):
                op = BinOp(args[1].value)
                return BinOpNode(op, args[0], args[2],
                                 **{'token': args[1], 'line': args[1].line, 'column': args[1].column})

            return get_bin_op_node
        else:
            def get_node(*args):
                props = {}
                if len(args) == 1 and isinstance(args[0], Token):
                    props['token'] = args[0]
                    props['line'] = args[0].line
                    props['column'] = args[0].column
                    args = [args[0].value]
                cls = eval(''.join(x.capitalize() for x in item.split('_')) + 'Node')
                return cls(*args, **props)

            return get_node


def parse(prog: str) -> StmtListNode:
    prog = parser.parse(str(prog))
    # print(prog.pretty('  '))
    prog = MelASTBuilder().transform(prog)
    return prog
