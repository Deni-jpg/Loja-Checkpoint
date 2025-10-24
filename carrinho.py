from datetime import datetime
from db import supabase 

def obter_ou_criar_carrinho(user_id):
    response = supabase.table("carrinhos").select("id").eq("user_id", user_id).eq("ativo", True).execute()
    if response.data:
        return response.data[0]["id"]
    
    novo = supabase.table("carrinhos").insert({"user_id": user_id}).execute()
    return novo.data[0]["id"]

def adicionar_item(carrinho_id, produto_id, quantidade, preco_unitario):
    supabase.table("itens_carrinho").insert({
        "carrinho_id": carrinho_id,
        "produto_id": produto_id,
        "quantidade": quantidade,
        "preco_unitario": preco_unitario
    }).execute()

def listar_itens(carrinho_id):
    response = supabase.table("itens_carrinho").select("produto_id", "quantidade", "preco_unitario").eq("carrinho_id", carrinho_id).execute()
    itens = response.data
    lista = []

    for item in itens:
        produto_resp = supabase.table("produtos").select("nome").eq("id", item["produto_id"]).execute()
        nome = produto_resp.data[0]["nome"] if produto_resp.data else "Desconhecido"
        lista.append({
            "nome": nome,
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
            "total": item["quantidade"] * item["preco_unitario"]
        })

    return lista

def remover_item(carrinho_id, produto_id):
    supabase.table("itens_carrinho").delete().eq("carrinho_id", carrinho_id).eq("produto_id", produto_id).execute()

def calcular_total(carrinho_id):
    response = supabase.table("itens_carrinho").select("quantidade", "preco_unitario").eq("carrinho_id", carrinho_id).execute()
    total = sum(item["quantidade"] * item["preco_unitario"] for item in response.data)
    return total

def finalizar_carrinho(carrinho_id, user_id):
    response = supabase.table("itens_carrinho").select("produto_id", "quantidade").eq("carrinho_id", carrinho_id).execute()
    itens = response.data

    for item in itens:
        for _ in range(item["quantidade"]):
            supabase.table("compras").insert({
                "user_id": user_id,
                "produto_id": item["produto_id"]
            }).execute()

    # Desativa o carrinho
    supabase.table("carrinhos").update({"ativo": False}).eq("id", carrinho_id).execute()
    print("✅ Compra finalizada com sucesso.")
