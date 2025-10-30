from db import supabase
from tabulate import tabulate
import json
import sys

def carregar_sessao():
    """Carrega o utilizador logado a partir do ficheiro sessao.json"""
    try:
        with open("sessao.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⛔ Precisas de fazer login antes de ver o histórico.")
        sys.exit()

def ver_historico_compras():
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

    from tabulate import tabulate
    headers = ["Produto", "Plataforma", "Qtd", "Preço Unit.", "Total", "Data da Compra"]
    print(tabulate(tabela, headers=headers, tablefmt="fancy_grid"))


if __name__ == "__main__":
    ver_historico_compras()
