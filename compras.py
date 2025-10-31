from carrinho import (
    obter_ou_criar_carrinho,
    adicionar_item,
    listar_itens,
    remover_item,
    calcular_total,
    finalizar_carrinho
)
from produtos_utils import listar_produtos
from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from pathlib import Path
from datetime import datetime
from notificacao_email import enviar_email
from tabulate import tabulate
import json
import sys
import historico_compras as hist

SESSAO_PATH = Path(__file__).parent / "sessao.json"

# === Sessão ===
def carregar_sessao():
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# === Notificação colorida ===
def notificar(msg, tipo="info"):
    cores = {
        "info": Fore.CYAN,
        "sucesso": Fore.GREEN,
        "erro": Fore.RED,
        "alerta": Fore.YELLOW
    }
    icones = {
        "info": "ℹ️",
        "sucesso": "✅",
        "erro": "❌",
        "alerta": "⚠️"
    }
    print(f"{cores.get(tipo, Fore.WHITE)}{icones.get(tipo, '💬')} {msg}{Style.RESET_ALL}")

# === Recomendar produto ===
def recomendar_produto(user_id):
    response = supabase.table("compras").select("produto_id").eq("user_id", user_id).execute()
    comprados = [c["produto_id"] for c in response.data or []]

    if comprados:
        ultimo = comprados[-1]
        produto = supabase.table("produtos").select("nome").eq("id", ultimo).execute().data
        if produto:
            notificar(f"💡 Já compraste {produto[0]['nome']}. Vê produtos semelhantes!", "info")

# === Menu de compras ===
def menu_compras():
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Compras")
        notificar("⛔ Precisas de fazer login primeiro.", "erro")
        rodape()
        input("\nENTER para voltar...")
        return

    user_id = sessao["id"]
    tipo = sessao["tipo"]
    nome = sessao["nome"]
    carrinho_id = obter_ou_criar_carrinho(user_id)

    while True:
        limpar_terminal()
        cabecalho("Menu de Compras", utilizador=nome)

        print(Fore.MAGENTA + "🛒 Loja Checkpoint — Compras" + Style.RESET_ALL)
        print("-" * 50)
        print("1️⃣  Ver produtos disponíveis")
        print("2️⃣  Adicionar produto ao carrinho")
        print("3️⃣  Ver carrinho")
        print("4️⃣  Remover item")
        print("5️⃣  Finalizar compra")
        print("6️⃣  Ver histórico simples")
        print("7️⃣  Ver histórico detalhado")
        if tipo == "admin":
            print("8️⃣  Ver todas as compras (admin)")
            print("9️⃣  Produtos mais comprados")
        print("0️⃣  Voltar")

        escolha = input("\n👉 Escolha uma opção: ").strip()

        if escolha == "1":
            listar_produtos()
            input("\nENTER para voltar...")

        elif escolha == "2":
            nome_busca = input("\n🔍 Nome do jogo: ").strip()
            plataforma = input("🎮 Plataforma (ENTER para todas): ").strip()
            animar_carregamento("A procurar produtos...")

            query = supabase.table("produtos").select("*").ilike("nome", f"%{nome_busca}%")
            if plataforma:
                query = query.eq("plataforma", plataforma)

            produtos = query.order("preco").execute().data

            if not produtos:
                notificar("❌ Nenhum produto encontrado.", "erro")
                input("\nENTER para voltar...")
                continue

            tabela = [[i+1, p["nome"], p["plataforma"], f"€{p['preco']:.2f}", p["stock"]] for i, p in enumerate(produtos)]
            print(tabulate(tabela, headers=["Nº", "Produto", "Plataforma", "Preço", "Stock"], tablefmt="fancy_grid"))

            try:
                idx = int(input("\nEscolha o número do produto: ")) - 1
                produto = produtos[idx]
                qtd = int(input("Quantidade: "))
                adicionar_item(carrinho_id, produto["id"], qtd, produto["preco"])
                notificar(f"{produto['nome']} adicionado ao carrinho.", "sucesso")
                if produto["stock"] <= 5:
                    notificar("⚠️ Stock baixo para este produto!", "alerta")
            except Exception:
                notificar("❌ Erro ao adicionar produto.", "erro")

            input("\nENTER para continuar...")

        elif escolha == "3":
            itens = listar_itens(carrinho_id)
            limpar_terminal()
            cabecalho("Carrinho Atual", utilizador=nome)

            if not itens:
                notificar("🛒 O teu carrinho está vazio.", "info")
            else:
                tabela = [
                    [i["nome"], i["quantidade"], f"€{i['preco_unitario']:.2f}", f"€{i['total']:.2f}"]
                    for i in itens
                ]
                print(tabulate(tabela, headers=["Produto", "Qtd", "Preço Unit.", "Total"], tablefmt="fancy_grid"))
                print(f"\n💰 Total: {Fore.YELLOW}€{calcular_total(carrinho_id):.2f}{Style.RESET_ALL}")

            rodape(utilizador=nome)
            input("\nENTER para voltar...")

        elif escolha == "4":
            termo = input("\nProduto a remover: ").strip()
            produto_resp = supabase.table("produtos").select("id").ilike("nome", f"%{termo}%").execute()
            if not produto_resp.data:
                notificar("❌ Produto não encontrado.", "erro")
                input("\nENTER para voltar...")
                continue
            remover_item(carrinho_id, produto_resp.data[0]["id"])
            notificar("🗑️ Produto removido do carrinho.", "alerta")
            input("\nENTER para voltar...")

        elif escolha == "5":
            finalizar_carrinho(carrinho_id, user_id)
            notificar("✅ Compra finalizada com sucesso!", "sucesso")
            input("\nENTER para voltar...")
            break

        elif escolha == "6":
            historico_simples(user_id, nome)

        elif escolha == "7":
            hist.ver_historico_compras()

        elif escolha == "8" and tipo == "admin":
            ver_todas_compras(nome)

        elif escolha == "9" and tipo == "admin":
            produtos_mais_comprados(nome)

        elif escolha == "0":
            break

        else:
            notificar("❌ Opção inválida.", "erro")
            input("\nENTER para continuar...")

# === Histórico simples ===
def historico_simples(user_id, nome):
    limpar_terminal()
    cabecalho("Histórico de Compras", utilizador=nome)
    animar_carregamento("A carregar histórico...")

    compras = supabase.table("compras").select("produto_id, data").eq("user_id", user_id).execute().data
    if not compras:
        notificar("📭 Ainda não fizeste nenhuma compra.", "info")
    else:
        tabela = []
        for c in compras:
            produto = supabase.table("produtos").select("nome").eq("id", c["produto_id"]).execute().data
            if produto:
                data_fmt = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
                tabela.append([produto[0]["nome"], data_fmt])
        print(tabulate(tabela, headers=["Produto", "Data"], tablefmt="fancy_grid"))

    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === Admin: ver todas as compras ===
def ver_todas_compras(nome):
    limpar_terminal()
    cabecalho("Todas as Compras", utilizador=nome)
    animar_carregamento("A carregar compras...")

    compras = supabase.table("compras").select("user_id, produto_id, data").execute().data
    if not compras:
        notificar("📭 Nenhuma compra registada.", "info")
    else:
        tabela = []
        for c in compras:
            prod = supabase.table("produtos").select("nome").eq("id", c["produto_id"]).execute().data
            nome_p = prod[0]["nome"] if prod else "Desconhecido"
            data_fmt = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
            tabela.append([c["user_id"], nome_p, data_fmt])
        print(tabulate(tabela, headers=["Utilizador", "Produto", "Data"], tablefmt="fancy_grid"))

    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === Admin: produtos mais comprados ===
def produtos_mais_comprados(nome):
    limpar_terminal()
    cabecalho("Top Produtos", utilizador=nome)
    animar_carregamento("A calcular ranking...")

    compras = supabase.table("compras").select("produto_id").execute().data
    if not compras:
        notificar("📭 Nenhuma compra registada.", "info")
        return

    contagem = {}
    for c in compras:
        pid = c["produto_id"]
        contagem[pid] = contagem.get(pid, 0) + 1

    top = sorted(contagem.items(), key=lambda x: x[1], reverse=True)[:10]
    tabela = []
    for pid, total in top:
        produto = supabase.table("produtos").select("nome").eq("id", pid).execute().data
        nome_p = produto[0]["nome"] if produto else "Desconhecido"
        tabela.append([nome_p, total])

    print(tabulate(tabela, headers=["Produto", "Nº Compras"], tablefmt="fancy_grid"))
    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === Execução direta ===
if __name__ == "__main__":
    menu_compras()
