"""
Módulo para visualização do histórico detalhado de compras do utilizador.

Este módulo:
- Carrega a sessão do utilizador a partir de ``sessao.json``.
- Obtém compras associadas ao utilizador na base de dados Supabase.
- Agrupa compras por produto, contando quantidades e última data de compra.
- Obtém informações do produto (nome, preço, plataforma).
- Apresenta uma tabela formatada no terminal com:
    - Nome do produto
    - Plataforma
    - Quantidade total adquirida
    - Preço unitário
    - Total gasto
    - Data mais recente da compra

É utilizado como ferramenta de consulta independente ou integrada no menu principal.
"""

from db import supabase
from tabulate import tabulate
import json
import sys


def carregar_sessao():
    """Carrega os dados do utilizador logado a partir do ficheiro ``sessao.json``.

    Se o ficheiro não existir, o programa informa o utilizador e termina.

    Returns:
        dict: Dados da sessão, contendo pelo menos ``"id"`` e ``"nome"``.

    Raises:
        SystemExit: Se o ficheiro ``sessao.json`` não existir, indicando que
        não há sessão ativa.
    """
    try:
        with open("sessao.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⛔ Precisas de fazer login antes de ver o histórico.")
        sys.exit()


def ver_historico_compras():
    """Mostra o histórico detalhado de compras do utilizador autenticado.

    Funcionamento:
        - Obtém o ID do utilizador através da sessão.
        - Consulta a tabela ``compras`` ordenando da mais recente para a mais antiga.
        - Agrupa compras por ``produto_id``, contando quantas unidades foram adquiridas
          e registando a data mais recente dessa compra.
        - Consulta as informações do produto na tabela ``produtos``.
        - Formata e exibe uma tabela com resumo das compras.

    A função imprime a tabela diretamente no terminal.

    Returns:
        None: Não devolve valores, apenas apresenta informação ao utilizador.
    """
    user = carregar_sessao()
    user_id = user["id"]

    print("\n📜 Histórico detalhado de compras\n")

    compras_resp = (
        supabase.table("compras")
        .select("id, produto_id, data")
        .eq("user_id", user_id)
        .order("data", desc=True)
        .execute()
    )

    compras = compras_resp.data or []
    if not compras:
        print("🕒 Ainda não realizaste nenhuma compra.")
        return

    # 🔹 Agrupar por produto_id
    agrupado = {}
    for c in compras:
        pid = c["produto_id"]
        data = c["data"]
        if pid not in agrupado:
            agrupado[pid] = {"quantidade": 0, "data": data}
        agrupado[pid]["quantidade"] += 1
        agrupado[pid]["data"] = max(agrupado[pid]["data"], data)  # mantém a data mais recente

    tabela = []
    for pid, info in agrupado.items():
        produto_resp = (
            supabase.table("produtos")
            .select("nome, preco, plataforma")
            .eq("id", pid)
            .execute()
        )

        produto = produto_resp.data[0] if produto_resp.data else None
        if produto:
            nome = produto["nome"]
            preco = float(produto["preco"])
            plataforma = produto["plataforma"] or "—"
        else:
            nome = "(Produto removido)"
            preco = 0.0
            plataforma = "—"

        qtd = info["quantidade"]
        total = preco * qtd
        data_fmt = info["data"][:19]

        tabela.append([nome, plataforma, f"{qtd}x", f"€{preco:.2f}", f"€{total:.2f}", data_fmt])

    headers = ["Produto", "Plataforma", "Qtd", "Preço Unit.", "Total", "Data da Compra"]
    print(tabulate(tabela, headers=headers, tablefmt="fancy_grid"))


if __name__ == "__main__":
    ver_historico_compras()
