from input import grafo_linear_bruto

grafo_linear_importado = grafo_linear_bruto

if not isinstance(grafo_linear_importado, list):
    raise TypeError("Erro de Contrato: O grafo importado da Fase 2 deve estar no formato de Lista.")

if len(grafo_linear_importado) == 0:
    raise ValueError("Erro de Consistência: A lista do grafo está vazia. Verifique a exportação da Fase 2.")

for index, aresta in enumerate(grafo_linear_importado):
    if not isinstance(aresta, list) or len(aresta) != 3:
        raise ValueError(f"Erro Estrutural na aresta do índice [{index}]: Cada item deve ser uma lista com exatamente 3 elementos [Palavra_A, Palavra_B, Força]. Dado encontrado: {aresta}")

    palavra_A = aresta[0]
    palavra_B = aresta[1]
    forca_conexao = aresta[2]

    if not isinstance(palavra_A, str) or not isinstance(palavra_B, str):
        raise TypeError(f"Erro de Tipo na aresta do índice [{index}]: Os nós identificadores devem ser strings textuais. Encontrado: {type(palavra_A)} e {type(palavra_B)}")

    if not isinstance(forca_conexao, (int, float)):
        raise TypeError(f"Erro de Tipo na aresta do índice [{index}]: A força da conexão deve ser numérica (int ou float). Encontrado: {type(forca_conexao)}")

    if forca_conexao <= 0:
        raise ValueError(f"Erro Lógico na aresta do índice [{index}]: A força de coocorrência deve ser maior que zero. Encontrado: {forca_conexao}")

print("[VALIDAÇÃO] Contrato da interface validado com 100% de integridade estrutural.")
print(f"[VALIDAÇÃO] Total de arestas aprovadas para a Fase 3: {len(grafo_linear_importado)}\n")

def exportar_grafo_auditado(dados_validados):
    return dados_validados

grafo_fase3_validado = exportar_grafo_auditado(grafo_linear_importado)