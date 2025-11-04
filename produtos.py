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

# === Validações & Leitura Segura ===
def _parse_float_pt(valor_str: str) -> float:
    """Aceita '9.99' ou '9,99' e converte para float."""
    return float(valor_str.replace(",", ".").strip())

def ler_texto_obrigatorio(prompt: str) -> str:
    """Lê texto não vazio."""
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        notificar("❌ Este campo é obrigatório.", "erro")

def ler_preco_positivo(prompt: str) -> float:
    """Lê um preço > 0 (aceita vírgulas)."""
    while True:
        bruto = input(prompt).strip()
        try:
            preco = _parse_float_pt(bruto)
            if preco <= 0:
                raise ValueError
            return preco
        except Exception:
            notificar("❌ Preço inválido. Introduz um número maior que 0 (ex.: 19,99).", "erro")

def ler_stock_nao_negativo(prompt: str) -> int:
    """Lê um stock inteiro >= 0."""
    while True:
        bruto = input(prompt).strip()
        try:
            stock = int(bruto)
            if stock < 0:
                raise ValueError
            return stock
        except Exception:
            notificar("❌ Stock inválido. Introduz um número inteiro igual ou maior que 0.", "erro")

def ler_id_inteiro(prompt: str) -> int:
    """Lê um ID inteiro válido."""
    while True:
        bruto = input(prompt).strip()
        try:
            return int(bruto)
        except Exception:
            notificar("❌ ID inválido. Introduz um número inteiro.", "erro")

def validar_produto(dados: dict) -> tuple[bool, list[str]]:
    """
    Validação final (defensiva) antes de escrever na BD.
    Retorna (ok: bool, erros: list[str])
    """
    erros = []

    nome = (dados.get("nome") or "").strip()
    if not nome:
        erros.append("Nome é obrigatório.")

    preco = dados.get("preco")
    if preco is None or not isinstance(preco, (int, float)) or preco <= 0:
        erros.append("Preço deve ser um número maior que 0.")

    stock = dados.get("stock")
    if stock is None or not isinstance(stock, int) or stock < 0:
        erros.append("Stock deve ser um inteiro igual ou maior que 0.")

    # Regras adicionais recomendadas
    plataforma = (dados.get("plataforma") or "").strip()
    if not plataforma:
        erros.append("Plataforma é obrigatória.")

    descricao = (dados.get("descricao") or "").strip()
    if len(descricao) > 1000:
        erros.append("Descrição não pode exceder 1000 caracteres.")

    return (len(erros) == 0, erros)

# === Operações ===
def adicionar_produto(nome_utilizador):
    limpar_terminal()
    cabecalho("Adicionar Produto", utilizador=nome_utilizador)

    nome = ler_texto_obrigatorio("🕹️ Nome: ")
    plataforma = ler_texto_obrigatorio("🎮 Plataforma: ")
    preco = ler_preco_positivo("💰 Preço (€): ")
    stock = ler_stock_nao_negativo("📦 Stock: ")
    descricao = input("📝 Descrição: ").strip()

    novo_produto = {
        "nome": nome,
        "plataforma": plataforma,
        "preco": preco,
        "stock": stock,
        "descricao": descricao
    }

    ok, erros = validar_produto(novo_produto)
    if not ok:
        notificar("❌ Não foi possível adicionar o produto devido a:", "erro")
        for e in erros:
            notificar(f"- {e}", "erro")
        rodape(utilizador=nome_utilizador)
        input("\nENTER para voltar...")
        return

    try:
        animar_carregamento("A adicionar produto...")
        supabase.table("produtos").insert(novo_produto).execute()
        notificar("✅ Produto adicionado com sucesso!", "sucesso")
    except Exception as ex:
        notificar(f"❌ Erro ao adicionar produto: {ex}", "erro")

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

def atualizar_produto(nome_utilizador):
    limpar_terminal()
    cabecalho("Atualizar Produto", utilizador=nome_utilizador)

    listar_produtos(modo="visual")

    produto_id = ler_id_inteiro("\n🆔 ID do produto a atualizar: ")

    nome = ler_texto_obrigatorio("🕹️ Novo nome: ")
    plataforma = ler_texto_obrigatorio("🎮 Nova plataforma: ")
    preco = ler_preco_positivo("💰 Novo preço (€): ")
    stock = ler_stock_nao_negativo("📦 Novo stock: ")
    descricao = input("📝 Nova descrição: ").strip()

    atualizacao = {
        "nome": nome,
        "plataforma": plataforma,
        "preco": preco,
        "stock": stock,
        "descricao": descricao
    }

    ok, erros = validar_produto(atualizacao)
    if not ok:
        notificar("❌ Não foi possível atualizar o produto devido a:", "erro")
        for e in erros:
            notificar(f"- {e}", "erro")
        rodape(utilizador=nome_utilizador)
        input("\nENTER para voltar...")
        return

    try:
        animar_carregamento("A atualizar produto...")
        supabase.table("produtos").update(atualizacao).eq("id", produto_id).execute()
        notificar("✅ Produto atualizado com sucesso!", "sucesso")
    except Exception as ex:
        notificar(f"❌ Erro ao atualizar produto: {ex}", "erro")

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

def remover_produto(nome_utilizador):
    limpar_terminal()
    cabecalho("Remover Produto", utilizador=nome_utilizador)

    listar_produtos(modo="visual")
    produto_id = ler_id_inteiro("\n🆔 ID do produto a remover: ")

    confirm = input("⚠️ Confirmar remoção? (s/n): ").strip().lower()
    if confirm == "s":
        try:
            animar_carregamento("A remover produto...")
            supabase.table("produtos").delete().eq("id", produto_id).execute()
            notificar("🗑️ Produto removido com sucesso!", "alerta")
        except Exception as ex:
            notificar(f"❌ Erro ao remover produto: {ex}", "erro")
    else:
        notificar("Remoção cancelada.", "info")

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

def listar_produtos_com_stock_baixo(nome_utilizador):
    limpar_terminal()
    cabecalho("Stock Baixo", utilizador=nome_utilizador)

    try:
        animar_carregamento("A verificar stock...")
        response = supabase.table("produtos").select("nome, stock").lt("stock", 3).execute()
        produtos = response.data or []
    except Exception as ex:
        produtos = []
        notificar(f"❌ Erro ao obter produtos: {ex}", "erro")

    if not produtos:
        notificar("📦 Nenhum produto com stock baixo!", "info")
    else:
        tabela = [[p.get("nome", ""), p.get("stock", 0)] for p in produtos]
        print(tabulate(tabela, headers=["Produto", "Stock"], tablefmt="fancy_grid"))

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")

def listar_produtos_mais_vendidos(nome_utilizador):
    limpar_terminal()
    cabecalho("Top 3 Produtos Mais Vendidos", utilizador=nome_utilizador)
    try:
        animar_carregamento("A carregar dados...")
        response = supabase.table("produtos").select("nome, vendas").order("vendas", desc=True).limit(3).execute()
        produtos = response.data or []
    except Exception as ex:
        produtos = []
        notificar(f"❌ Erro ao obter ranking de vendas: {ex}", "erro")

    if not produtos:
        notificar("📭 Nenhum produto registado ainda.", "info")
    else:
        tabela = [[i + 1, p.get("nome", ""), p.get("vendas", 0)] for i, p in enumerate(produtos)]
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
                case "1":
                    adicionar_produto(nome)
                case "2":
                    listar_produtos(modo="visual")
                    input("\nENTER para voltar...")
                case "3":
                    atualizar_produto(nome)
                case "4":
                    remover_produto(nome)
                case "5":
                    listar_produtos_com_stock_baixo(nome)
                case "6":
                    listar_produtos_mais_vendidos(nome)
                case "0":
                    break
                case _:
                    notificar("❌ Opção inválida.", "erro")
                    input("\nENTER para continuar...")

        else:  # Cliente
            print(Fore.MAGENTA + "🎮 Catálogo de Produtos" + Style.RESET_ALL)
            print("-" * 50)
            print("1️⃣  Ver produtos disponíveis")
            print("2️⃣  Ver produtos mais vendidos")
            print("0️⃣  Voltar")

            escolha = input("\n👉 Escolha uma opção: ").strip()
            if escolha == "1":
                listar_produtos(modo="visual", utilizador=nome)
                input("\nENTER para voltar...")
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