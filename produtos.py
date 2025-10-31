from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from tabulate import tabulate
from produtos_utils import listar_produtos  # usa o utilitário visual/dados
from pathlib import Path
import json, sys

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

# === Operações ===
def adicionar_produto(nome_utilizador):
    limpar_terminal()
    cabecalho("Adicionar Produto", utilizador=nome_utilizador)

    nome = input("🕹️ Nome: ").strip()
    plataforma = input("🎮 Plataforma: ").strip()
    preco = float(input("💰 Preço (€): "))
    stock = int(input("📦 Stock: "))
    descricao = input("📝 Descrição: ")

    animar_carregamento("A adicionar produto...")
    supabase.table("produtos").insert({
        "nome": nome,
        "plataforma": plataforma,
        "preco": preco,
        "stock": stock,
        "descricao": descricao
    }).execute()

    notificar("✅ Produto adicionado com sucesso!", "sucesso")
    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

def atualizar_produto(nome_utilizador):
    limpar_terminal()
    cabecalho("Atualizar Produto", utilizador=nome_utilizador)

    listar_produtos(modo="visual")

    try:
        produto_id = int(input("\n🆔 ID do produto a atualizar: "))
    except ValueError:
        notificar("❌ ID inválido.", "erro")
        return

    nome = input("🕹️ Novo nome: ")
    plataforma = input("🎮 Nova plataforma: ")
    preco = float(input("💰 Novo preço (€): "))
    stock = int(input("📦 Novo stock: "))
    descricao = input("📝 Nova descrição: ")

    animar_carregamento("A atualizar produto...")
    supabase.table("produtos").update({
        "nome": nome,
        "plataforma": plataforma,
        "preco": preco,
        "stock": stock,
        "descricao": descricao
    }).eq("id", produto_id).execute()

    notificar("✅ Produto atualizado com sucesso!", "sucesso")
    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

def remover_produto(nome_utilizador):
    limpar_terminal()
    cabecalho("Remover Produto", utilizador=nome_utilizador)

    listar_produtos(modo="visual")
    try:
        produto_id = int(input("\n🆔 ID do produto a remover: "))
    except ValueError:
        notificar("❌ ID inválido.", "erro")
        return

    if input("⚠️ Confirmar remoção? (s/n): ").lower() == "s":
        animar_carregamento("A remover produto...")
        supabase.table("produtos").delete().eq("id", produto_id).execute()
        notificar("🗑️ Produto removido com sucesso!", "alerta")
    else:
        notificar("Remoção cancelada.", "info")

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

def listar_produtos_com_stock_baixo(nome_utilizador):
    limpar_terminal()
    cabecalho("Stock Baixo", utilizador=nome_utilizador)

    animar_carregamento("A verificar stock...")
    response = supabase.table("produtos").select("nome, stock").lt("stock", 3).execute()
    produtos = response.data or []

    if not produtos:
        notificar("📦 Nenhum produto com stock baixo!", "info")
    else:
        tabela = [[p["nome"], p["stock"]] for p in produtos]
        print(tabulate(tabela, headers=["Produto", "Stock"], tablefmt="fancy_grid"))

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

def listar_produtos_mais_vendidos(nome_utilizador):
    limpar_terminal()
    cabecalho("Top 3 Produtos Mais Vendidos", utilizador=nome_utilizador)
    animar_carregamento("A carregar dados...")

    response = supabase.table("produtos").select("nome, vendas").order("vendas", desc=True).limit(3).execute()
    produtos = response.data or []

    if not produtos:
        notificar("📭 Nenhum produto registado ainda.", "info")
    else:
        tabela = [[i+1, p["nome"], p["vendas"]] for i, p in enumerate(produtos)]
        print(tabulate(tabela, headers=["#", "Produto", "Vendas"], tablefmt="fancy_grid"))

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

# === Menu principal ===
def menu_produtos():
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Produtos")
        notificar("⛔ Precisas de fazer login para aceder ao menu de produtos.", "erro")
        rodape()
        input("\nENTER para voltar...")
        return

    nome = sessao["nome"]
    tipo = sessao["tipo"]

    while True:
        limpar_terminal()
        cabecalho("Menu de Produtos", utilizador=nome)

        if tipo == "admin":
            print(Fore.CYAN + "⚙️  Gestão de Produtos (Admin)" + Style.RESET_ALL)
            print("-" * 50)
            print("1️⃣  Adicionar produto")
            print("2️⃣  Listar produtos")
            print("3️⃣  Atualizar produto")
            print("4️⃣  Remover produto")
            print("5️⃣  Ver produtos com stock baixo")
            print("6️⃣  Top 3 produtos mais vendidos")
            print("0️⃣  Voltar")
            escolha = input("\n👉 Escolha uma opção: ").strip()

            match escolha:
                case "1": adicionar_produto(nome)
                case "2": listar_produtos(modo="visual")
                case "3": atualizar_produto(nome)
                case "4": remover_produto(nome)
                case "5": listar_produtos_com_stock_baixo(nome)
                case "6": listar_produtos_mais_vendidos(nome)
                case "0": break
                case _: notificar("❌ Opção inválida.", "erro"); input("\nENTER para continuar...")

        else:  # Cliente
            print(Fore.MAGENTA + "🎮 Catálogo de Produtos" + Style.RESET_ALL)
            print("-" * 50)
            print("1️⃣  Ver produtos disponíveis")
            print("2️⃣  Ver produtos mais vendidos")
            print("0️⃣  Voltar")

            escolha = input("\n👉 Escolha uma opção: ").strip()
            if escolha == "1":
                listar_produtos(modo="visual", utilizador=nome)
            elif escolha == "2":
                listar_produtos_mais_vendidos(nome)
            elif escolha == "0":
                break
            else:
                notificar("❌ Opção inválida.", "erro")
                input("\nENTER para continuar...")

# === Execução direta ===
if __name__ == "__main__":
    menu_produtos()
