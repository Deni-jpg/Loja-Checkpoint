from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from tabulate import tabulate
import json, sys

def carregar_sessao():
    try:
        with open("sessao.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def escolher_jogo(excluir_ids=None):
    termo = input("\n🔍 Nome do jogo (ou ENTER para listar todos): ").strip()

    query = supabase.table("produtos").select("id, nome, preco, plataforma")
    if termo:
        query = query.ilike("nome", f"%{termo}%")
    if excluir_ids:
        query = query.not_.in_("id", excluir_ids)

    animar_carregamento("A carregar jogos...")
    produtos = query.execute().data or []
    if not produtos:
        print("❌ Nenhum jogo encontrado.")
        return None

    tabela = [[i+1, p["nome"], p["plataforma"], f"€{float(p['preco']):.2f}"] for i, p in enumerate(produtos)]
    print(tabulate(tabela, headers=["Nº", "Nome", "Plataforma", "Preço"], tablefmt="fancy_grid"))

    try:
        idx = int(input("\nEscolha o número do jogo: ")) - 1
        return produtos[idx]
    except:
        print("⚠️ Escolha inválida.")
        return None

def comparar_jogos():
    sessao = carregar_sessao()
    if not sessao:
        print("⛔ Precisas de fazer login para comparar jogos.")
        sys.exit()

    nome = sessao["nome"]
    limpar_terminal()
    cabecalho("Comparar Jogos", utilizador=nome)

    print(Fore.MAGENTA + "\n🎮 Comparador de Jogos" + Style.RESET_ALL)
    print("-" * 50)

    jogo1 = escolher_jogo()
    if not jogo1:
        return
    jogo2 = escolher_jogo(excluir_ids=[jogo1["id"]])
    if not jogo2:
        return

    selecionados = [jogo1, jogo2]
    while True:
        extra = input("➕ Adicionar outro jogo? (s/n): ").lower().strip()
        if extra == "s":
            novo = escolher_jogo(excluir_ids=[p["id"] for p in selecionados])
            if novo:
                selecionados.append(novo)
        else:
            break

    animar_carregamento("A gerar comparação...")

    for p in selecionados:
        avals = supabase.table("avaliacoes").select("estrelas").eq("produto_id", p["id"]).execute().data or []
        if avals:
            media = sum(a["estrelas"] for a in avals) / len(avals)
            p["avaliacao"] = f"{media:.1f} ⭐"
        else:
            p["avaliacao"] = "Sem avaliações"

    tabela = [[p["nome"], f"€{p['preco']:.2f}", p["plataforma"], p["avaliacao"]] for p in selecionados]
    print("\n🆚 Comparação de Jogos:\n")
    print(tabulate(tabela, headers=["Nome", "Preço", "Plataforma", "Avaliação Média"], tablefmt="fancy_grid"))

    rodape(utilizador=nome)
    input("\nENTER para voltar...")

if __name__ == "__main__":
    comparar_jogos()
