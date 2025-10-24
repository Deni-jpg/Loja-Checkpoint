from db import supabase

def listar_produtos():
    response = supabase.table("produtos").select("*").execute()
    if response.data:
        produtos = response.data
        for i, produto in enumerate(response.data, start=1):
            print(f"{i}. {produto['nome']} ({produto['plataforma']}) - {produto['preco']:.2f}€ | Stock: {produto['stock']}")

def obter_produto_por_id(produto_id):
    response = supabase.table("produtos").select("*").eq("id", produto_id).execute()
    return response.data[0] if response.data else None