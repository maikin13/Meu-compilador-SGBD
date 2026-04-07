import os

def carregar_dados(arquivo='empregados.txt'):
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(diretorio_script, arquivo)
    
    if not os.path.exists(caminho_completo):
        print(f"ERRO: O arquivo '{arquivo}' não foi encontrado na pasta!")
        return []

    dados = []
    with open(caminho_completo, 'r', encoding='utf-8') as arquivo:
        for linha_bruta in arquivo:
            linha_limpa = linha_bruta.strip()
            if not linha_limpa: continue
                
            pedacos = linha_limpa.split(';')
            if len(pedacos) == 6:
                try:
                    dados.append({
                        'nome': pedacos[0].strip(),
                        'cpf': pedacos[1].strip(),
                        'matricula': pedacos[2].strip(),
                        'sexo': pedacos[3].strip(),
                        'salario': float(pedacos[4]),
                        'idade': int(pedacos[5])
                    })
                except Exception:
                    pass
    return dados

def avaliar_condicao(linha, condicao):
    if not condicao: return True 
    if not isinstance(condicao, tuple): return False
        
    if len(condicao) == 3 and condicao[0] in ('AND', 'OR'):
        op_logico = condicao[0]
        esq = avaliar_condicao(linha, condicao[1])
        dir = avaliar_condicao(linha, condicao[2])
        if op_logico == 'AND': return esq and dir
        if op_logico == 'OR': return esq or dir

    coluna, operador, valor = condicao
    valor_linha = linha.get(coluna.lower().strip())
    if valor_linha is None: return False
    
    try:
        if operador == '>': return valor_linha > valor
        elif operador == '<': return valor_linha < valor
        elif operador == '=': return valor_linha == valor
        elif operador == '>=': return valor_linha >= valor
        elif operador == '<=': return valor_linha <= valor
        elif operador == '!=': return valor_linha != valor
    except TypeError:
        return False
    return False

def executar_query(dados, colunas_select, filtro_where, order_by=None, limit_q=None):
    if not dados: return [] # Segurança caso não tenha dados

    # WHERE
    dados_filtrados = [linha for linha in dados if avaliar_condicao(linha, filtro_where)]

    # ORDER BY
    if order_by and dados_filtrados:
        coluna_ord, direcao = order_by
        coluna_ord = coluna_ord.lower().strip()
        reverso = (direcao == 'DESC')
        dados_filtrados.sort(key=lambda x: x.get(coluna_ord, 0) if isinstance(x.get(coluna_ord), (int, float)) else str(x.get(coluna_ord, '')), reverse=reverso)

    # SELECT
    tem_agregacao = any(isinstance(c, tuple) and c[0] in ('MAX', 'MIN') for c in colunas_select if c != '*')

    if colunas_select == ['*']:
        resultados_finais = dados_filtrados
    elif tem_agregacao:
        if not dados_filtrados: return []
        linha_agregada = {}
        for tipo, col in colunas_select:
            col_limpa = col.lower().strip()
            if tipo == 'SIMPLE':
                linha_agregada[col_limpa] = dados_filtrados[0].get(col_limpa)
            elif tipo == 'MAX':
                valores = [l.get(col_limpa) for l in dados_filtrados if l.get(col_limpa) is not None]
                linha_agregada[f"MAX({col_limpa})"] = max(valores) if valores else None
            elif tipo == 'MIN':
                valores = [l.get(col_limpa) for l in dados_filtrados if l.get(col_limpa) is not None]
                linha_agregada[f"MIN({col_limpa})"] = min(valores) if valores else None
        resultados_finais = [linha_agregada]
    else:
        resultados_finais = []
        for linha in dados_filtrados:
            linha_projetada = {col.lower().strip(): linha[col.lower().strip()] for tipo, col in colunas_select if col.lower().strip() in linha}
            if linha_projetada: resultados_finais.append(linha_projetada)

    # LIMIT
    if limit_q is not None:
        resultados_finais = resultados_finais[:limit_q]
            
    return resultados_finais