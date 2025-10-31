from db import supabase
from pathlib import Path
from datetime import datetime
import json
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style

SESSAO_PATH = Path(__file__).parent / "sessao.json"

# === FUNÇÕES DE SESSÃO ===
def carregar_sessao():
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# === NOTIFICAÇÕES COLORIDAS ===
def notificar(mensagem, tipo="info"):
    cores = {
        "info": Fore.CYAN,
        "sucesso": Fore.GREEN,
        "erro": Fore.RED,
        "alerta": Fore.YELLOW
    }
    cor = cores.get(tipo, Fore.WHITE)
    print(f"{cor}🔔 {mensagem}{Style.RESET_ALL}")

# === MENU WISHLIST ===
def menu_wishlist():
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Wishlist")
        notificar("⛔ Precisas de fazer login para aceder à wishlist.", "erro")
        rodape()
        input("\n🔙 Pressiona ENTER para voltar...")
        return

    user_id = sessao["id"]
    nome = sessao.get("nome", "Utilizador")

    while True:
        limpar_terminal()
        cabecalho("Wishlist", utilizador=nome)

        print(Fore.MAGENTA + "🎁 Gestão da tua Wishlist" + Style.RESET_ALL)
        print("-" * 50)
        print("1️⃣  Adicionar produto à wishlist")
        print("2️⃣  Ver wishlist")
        print("3️⃣  Remover produto da wishlist")
        print("0️⃣  Voltar")
        escolha = input("\n👉 Escolha uma opção: ").strip()

        if escolha == "1":
            adicionar_produto_wishlist(user_id, nome)
        elif escolha == "2":
            ver_wishlist(user_id, nome)
        elif escolha == "3":
            remover_produto_wishlist(user_id, nome)
        elif escolha == "0":
            break
        else:
            notificar("❌ Opção inválida.", "erro")
            input("\n🔙 ENTER para continuar...")

# === ➕ Adicionar produto ===
def adicionar_produto_wishlist(user_id, nome):
    limpar_terminal()
    cabecalho("Adicionar à Wishlist", utilizador=nome)

    termo = input("🔎 Digite parte do nome do produto: ").strip()
    animar_carregamento("A procurar produtos...")
    produtos = (
        supabase.table("produtos")
        .select("id, nome, preco, plataforma")
        .ilike("nome", f"%{termo}%")
        .execute()
        .data
    )

    if not produtos:
        notificar("❌ Nenhum produto encontrado.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    print("\n🎮 Produtos encontrados:\n")
    for i, p in enumerate(produtos, start=1):
        print(f"{i}. {p['nome']} ({p['plataforma']}) — €{p['preco']:.2f}")

    try:
        escolha = int(input("\n👉 Escolha o número do produto: "))
        produto = produtos[escolha - 1]

        # Verifica se já existe
        existe = (
            supabase.table("wishlist")
            .select("id")
            .eq("user_id", user_id)
            .eq("produto_id", produto["id"])
            .execute()
        )

        if existe.data:
            notificar("⚠️ Este produto já está na tua wishlist.", "alerta")
            rodape(utilizador=nome)
            input("\nENTER para voltar...")
            return

        supabase.table("wishlist").insert({
            "user_id": user_id,
            "produto_id": produto["id"],
            "adicionado_em": datetime.now().isoformat()
        }).execute()

        notificar(f"✅ {produto['nome']} adicionado à wishlist!", "sucesso")

    except (ValueError, IndexError):
        notificar("❌ Escolha inválida.", "erro")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === 👀 Ver wishlist ===
def ver_wishlist(user_id, nome):
    limpar_terminal()
    cabecalho("Wishlist — Ver Itens", utilizador=nome)

    animar_carregamento("A carregar wishlist...")
    response = (
        supabase.table("wishlist")
        .select("produto_id, adicionado_em")
        .eq("user_id", user_id)
        .order("adicionado_em", desc=True)
        .execute()
    )

    data = response.data or []
    if not data:
        notificar("📭 A tua wishlist está vazia.", "info")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    print("\n🎁 Itens na tua wishlist:\n")
    for item in data:
        produto_resp = (
            supabase.table("produtos")
            .select("nome, preco, plataforma")
            .eq("id", item["produto_id"])
            .execute()
        )
        if not produto_resp.data:
            continue
        produto = produto_resp.data[0]
        print(
            f"• {produto['nome']} ({produto['plataforma']}) — €{produto['preco']:.2f}"
        )

    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === ❌ Remover produto ===
def remover_produto_wishlist(user_id, nome):
    limpar_terminal()
    cabecalho("Remover da Wishlist", utilizador=nome)
    
    termo = input("🗑️  Digite parte do nome do produto a remover: ").strip()
    animar_carregamento("A procurar produto para remover...")
    produtos = (
        supabase.table("produtos")
        .select("id, nome")
        .ilike("nome", f"%{termo}%")
        .execute()
        .data
    )

    if not produtos:
        notificar("❌ Nenhum produto encontrado com esse nome.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    ids = [p["id"] for p in produtos]
    supabase.table("wishlist").delete().eq("user_id", user_id).in_("produto_id", ids).execute()
    notificar("🗑️ Produto removido da wishlist.", "alerta")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === EXECUÇÃO DIRETA ===
if __name__ == "__main__":
    menu_wishlist()
