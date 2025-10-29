from db import supabase
from datetime import datetime
import json
import sys

def carregar_sessao():
    try:
        with open("sessao.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def avaliar_produto(user_id):
    produto = input("\nProduto que quer avaliar: ")
    response = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute()
    produtos = response.data

    if not produtos:
        print("❌ Produto não encontrado.")
        return

    for i, p in enumerate(produtos):
        print(f"{i + 1}. {p['nome']}")
    try:
        index = int(input("\nEscolha o número do produto: ")) - 1
        produto_id = produtos[index]["id"]
    except:
        print("Escolha inválida.")
        return

    # Verifica se o utilizador já comprou o produto
    compras = supabase.table("compras").select("id").eq("user_id", user_id).eq("produto_id", produto_id).execute()
    if not compras.data:
        print("⚠️ Só podes avaliar produtos que já compraste.")
        return

    # Verifica se já avaliou
    ja_avaliou = supabase.table("avaliacoes").select("*").eq("user_id", user_id).eq("produto_id", produto_id).execute()
    if ja_avaliou.data:
        print("⚠️ Já avaliou este produto. A avaliação será atualizada.")

    try:
        estrelas = int(input("Classificação (1 a 5 estrelas): "))
        if estrelas < 1 or estrelas > 5:
            raise ValueError
    except ValueError:
        print("Valor inválido.")
        return

    comentario = input("Comentário (opcional): ").strip()

    supabase.table("avaliacoes").upsert({
        "user_id": user_id,
        "produto_id": produto_id,
        "estrelas": estrelas,
        "comentario": comentario
    }).execute()

    print(f"⭐ Avaliação registada: {estrelas} estrelas para {produtos[index]['nome']}")

def ver_media_avaliacoes():
    produtos = supabase.table("produtos").select("id", "nome").execute().data
    print("\n📊 Médias de Avaliações:")
    for p in produtos:
        avals = supabase.table("avaliacoes").select("estrelas").eq("produto_id", p["id"]).execute().data
        if avals:
            media = sum(a["estrelas"] for a in avals) / len(avals)
            print(f"{p['nome']} → ⭐ {media:.1f}/5 ({len(avals)} avaliações)")
        else:
            print(f"{p['nome']} → sem avaliações ainda.")

# 🚪 Entrada principal
user = carregar_sessao()
if not user:
    print("⛔ Precisas de fazer login para avaliar.")
    sys.exit()

print(f"\n⭐ Bem-vindo {user['nome']} ({user['tipo']})")

if user["tipo"] == "cliente":
    print("1 -> Avaliar produto")
    print("2 -> Ver médias de avaliação")
    escolha = input("Opção: ").strip()
    if escolha == "1":
        avaliar_produto(user["id"])
    elif escolha == "2":
        ver_media_avaliacoes()
    else:
        print("Opção inválida.")
elif user["tipo"] == "admin":
    ver_media_avaliacoes()
