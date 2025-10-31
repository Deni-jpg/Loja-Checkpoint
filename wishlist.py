from db import supabase
from pathlib import Path
import json
from datetime import datetime
from produtos_utils import listar_produtos

SESSAO_PATH = Path(__file__).parent / "sessao.json"

def carregar_sessao():
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def notificar(mensagem, tipo="info"):
    cores = {
        "info": "\033[94m",
        "sucesso": "\033[92m",
        "erro": "\033[91m",
        "alerta": "\033[93m"
    }
    cor = cores.get(tipo, "\033[0m")
    print(f"{cor}🔔 {mensagem}\033[0m")

def menu_wishlist():
    sessao = carregar_sessao()
    if not sessao:
        notificar("⛔ Precisas de fazer login para aceder à wishlist.", "erro")
        return

    user_id = sessao["id"]

    while True:
        print("\n🎁 Menu Wishlist")
        print("1. Adicionar produto à wishlist")
        print("2. Ver wishlist")
        print("3. Remover produto da wishlist")
        print("0. Voltar")
        escolha = input("Escolha: ").strip()

        if escolha == "1":
            adicionar_produto_wishlist(user_id)
        elif escolha == "2":
            ver_wishlist(user_id)
        elif escolha == "3":
            remover_produto_wishlist(user_id)
        elif escolha == "0":
            break
        else:
            notificar("❌ Opção inválida.", "erro")


# ➕ Adicionar produto
def adicionar_produto_wishlist(user_id):
    termo = input("Digite parte do nome do produto: ").strip()
    produtos = supabase.table("produtos").select("id, nome, preco, plataforma").ilike("nome", f"%{termo}%").execute().data

    if not produtos:
        notificar("Nenhum produto encontrado.", "erro")
        return

    print("\n🔍 Produtos encontrados:")
    for i, p in enumerate(produtos, start=1):
        print(f"{i}. {p['nome']} ({p['plataforma']}) - €{p['preco']:.2f}")

    try:
        escolha = int(input("Escolha o número do produto para adicionar: "))
        produto = produtos[escolha - 1]

        # Verifica se já existe
        existe = supabase.table("wishlist").select("id").eq("user_id", user_id).eq("produto_id", produto["id"]).execute()
        if existe.data:
            notificar("⚠️ Este produto já está na tua wishlist.", "alerta")
            return

        supabase.table("wishlist").insert({
            "user_id": user_id,
            "produto_id": produto["id"],
            "adicionado_em": datetime.now().isoformat()
        }).execute()

        notificar(f"✅ {produto['nome']} adicionado à wishlist!", "sucesso")

    except (ValueError, IndexError):
        notificar("❌ Escolha inválida.", "erro")


# 👀 Ver wishlist
def ver_wishlist(user_id):
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
        return

    print("\n🎁 Tua wishlist:")
    for item in data:
        produto_resp = supabase.table("produtos").select("nome, preco, plataforma").eq("id", item["produto_id"]).execute()
        if not produto_resp.data:
            continue
        produto = produto_resp.data[0]
        print(f"- {produto['nome']} ({produto['plataforma']}) - €{produto['preco']:.2f}")

# ❌ Remover produto
def remover_produto_wishlist(user_id):
    ver_wishlist(user_id)
    termo = input("\nDigite parte do nome do produto a remover: ").strip()

    produtos = supabase.table("produtos").select("id, nome").ilike("nome", f"%{termo}%").execute().data
    if not produtos:
        notificar("❌ Nenhum produto encontrado com esse nome.", "erro")
        return

    ids = [p["id"] for p in produtos]
    supabase.table("wishlist").delete().eq("user_id", user_id).in_("produto_id", ids).execute()
    notificar("🗑️ Produto removido da wishlist.", "alerta")


if __name__ == "__main__":
    menu_wishlist()
