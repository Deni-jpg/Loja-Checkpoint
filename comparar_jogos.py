from db import supabase
from tabulate import tabulate
import json
import sys

def carregar_sessao():
    try:
        with open("sessao.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def escolher_jogo(excluir_ids=None):
    """Permite ao utilizador procurar e escolher um jogo, com exclusão opcional."""
    termo = input("\n🔍 Digite parte do nome do jogo (ou ENTER para listar todos): ").strip()

    query = supabase.table("produtos").select("id, nome, preco, plataforma")
    if termo:
        query = query.ilike("nome", f"%{termo}%")
    if excluir_ids:
        query = query.not_.in_("id", excluir_ids)
    response = query.execute()

    produtos = response.data or []
    if not produtos:
        print("❌ Nenhum produto encontrado.")
        return None

    print("\n📋 Jogos disponíveis:")
    for i, p in enumerate(produtos, start=1):
        preco_fmt = f"€{float(p['preco']):.2f}" if p.get("preco") is not None else "—"
        print(f"{i}. {p['nome']} ({p['plataforma']}) - {preco_fmt}")

    try:
        escolha = int(input("\nEscolhe o número do jogo: ").strip())
        if 1 <= escolha <= len(produtos):
            return produtos[escolha - 1]
        else:
            print("⚠️ Número inválido.")
            return None
    except ValueError:
        print("⚠️ Escolha inválida.")
        return None


def comparar_jogos():
    user = carregar_sessao()
    if not user:
        print("⛔ Precisas de fazer login para comparar jogos.")
        sys.exit()

    print("\n🎮 Comparar Jogos")

    # Primeiro jogo
    jogo1 = None
    while not jogo1:
        jogo1 = escolher_jogo()

    # Segundo jogo
    jogo2 = None
    while not jogo2:
        jogo2 = escolher_jogo(excluir_ids=[jogo1["id"]])

    selecionados = [jogo1, jogo2]

    # Pergunta se quer comparar mais
    while True:
        extra = input("➕ Queres adicionar outro jogo à comparação? (s/n): ").lower().strip()
        if extra == "s":
            novo = escolher_jogo(excluir_ids=[p["id"] for p in selecionados])
            if novo:
                selecionados.append(novo)
        else:
            break

    print("\n🕒 A gerar comparação...")

    # Buscar média de avaliações para cada jogo
    for p in selecionados:
        avals = (
            supabase.table("avaliacoes")
            .select("estrelas")
            .eq("produto_id", p["id"])
            .execute()
            .data
            or []
        )
        if avals:
            media = sum(a["estrelas"] for a in avals) / len(avals)
            p["avaliacao"] = f"{media:.1f} ⭐"
        else:
            p["avaliacao"] = "Sem avaliações"

    # Construir tabela
    tabela = []
    for p in selecionados:
        preco_fmt = f"€{float(p['preco']):.2f}" if p.get("preco") is not None else "—"
        tabela.append([p["nome"], preco_fmt, p["plataforma"], p["avaliacao"]])

    headers = ["Nome do Jogo", "Preço", "Plataforma", "Avaliação Média"]

    print("\n🆚 Comparação de Jogos:\n")
    print(tabulate(tabela, headers=headers, tablefmt="fancy_grid"))


if __name__ == "__main__":
    comparar_jogos()
