from lark import Lark, Transformer

sql_grammar = """
    ?start: query
    query: _SELECT column_list _FROM WORD where_clause? order_clause? limit_clause?
    
    where_clause: _WHERE condition
    order_clause: _ORDER _BY WORD [direcao]
    
    ?direcao: "ASC"i -> dir_asc
            | "DESC"i -> dir_desc

    limit_clause: _LIMIT SIGNED_NUMBER

    ?column_list: "*" -> select_all
                | col_item ("," col_item)* -> select_cols

    ?col_item: WORD -> col_simple
             | _MAX "(" WORD ")" -> col_max
             | _MIN "(" WORD ")" -> col_min
               
    ?condition: cond_or
    ?cond_or: cond_and (_OR cond_and)*
    ?cond_and: base_cond (_AND base_cond)*
    
    ?base_cond: WORD operator value -> simple_cond
              | "(" condition ")" -> paren_cond
    
    !operator: "=" | ">" | "<" | ">=" | "<=" | "!="
    
    ?value: SIGNED_NUMBER -> number
          | ESCAPED_STRING -> string
          | "'" /[^']+/ "'" -> string_word

    _SELECT: "SELECT"i
    _FROM: "FROM"i
    _WHERE: "WHERE"i
    _AND: "AND"i
    _OR: "OR"i
    _ORDER: "ORDER"i
    _BY: "BY"i
    _LIMIT: "LIMIT"i
    _MAX: "MAX"i
    _MIN: "MIN"i

    %import common.WORD
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""

class SQLTransformer(Transformer):
    def query(self, items):
        colunas, tabela = items[0], str(items[1])
        condicao, order_by, limit = None, None, None

        for item in items[2:]:
            if hasattr(item, 'data'):
                if item.data == 'where_clause': condicao = item.children[0]
                elif item.data == 'order_clause':
                    direcao = str(item.children[1]) if len(item.children) > 1 else "ASC"
                    order_by = (str(item.children[0]), direcao)
                elif item.data == 'limit_clause': limit = int(item.children[0])

        return colunas, tabela, condicao, order_by, limit

    def select_all(self, items): return ['*']
    def select_cols(self, items): return [i for i in items if isinstance(i, tuple)]
    def dir_asc(self, items): return "ASC"
    def dir_desc(self, items): return "DESC"
    def col_simple(self, items): return ('SIMPLE', str(items[0]).strip())
    def col_max(self, items): return ('MAX', str(items[0]).strip())
    def col_min(self, items): return ('MIN', str(items[0]).strip())
    def where_clause(self, items): return items[0]
    
    def simple_cond(self, items): return (str(items[0]), str(items[1].children[0]), items[2])
    def paren_cond(self, items): return items[0]

    def cond_and(self, items):
        res = items[0]
        for item in items[1:]: res = ('AND', res, item)
        return res
        
    def cond_or(self, items):
        res = items[0]
        for item in items[1:]: res = ('OR', res, item)
        return res

    def number(self, items): return float(items[0])
    def string(self, items): return str(items[0])[1:-1]
    def string_word(self, items): return str(items[0])

_parser = Lark(sql_grammar, parser='lalr', transformer=SQLTransformer())

def analisar_query(query_string):
    try:
        return _parser.parse(query_string)
    except Exception as e:
        return f"Erro de Sintaxe: \n{e}\n\n. Verifique o comando digitado!"