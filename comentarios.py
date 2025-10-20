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

def fazer_comentario(user_id):
    produto = input("\nQual o produto que quer comentar: ")
    response = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute()
    produtos = response.data

    if not produtos:
        print("Produto não encontrado.")
        return

    if len(produtos) > 1:
        print("\nProdutos encontrados:")
        for i, p in enumerate(produtos):
            print(f"{i + 1}. {p['nome']}")
        try:
            index = int(input("\nNúmero do produto: ")) - 1
            produto_id = produtos[index]["id"]
        except:
            print("Escolha inválida.")
            return
    else:
        produto_id = produtos[0]["id"]

    texto = input("\nEscreva o seu comentário: ")

    supabase.table("comentarios").insert({
        "user_id": user_id,
        "texto": texto,
        "produto_id": produto_id,
        "aprovado": False
    }).execute()

    print("Comentário adicionado com sucesso!")



def julgar_comentario():

    response = (
        supabase.table("comentarios")
        .select("*")
        .execute()
    )
    print(response)

def listar_comentario_por_produto():
    produto = input("Produto para ver comentários: ")
    produtos = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute().data

    if not produtos:
        print("Produto não encontrado.")
        return

    for i, p in enumerate(produtos):
        print(f"{i + 1}. {p['nome']}")
    try:
        index = int(input("\nNúmero do produto: ")) - 1
        produto_id = produtos[index]["id"]
    except:
        print("Escolha inválida.")
        return

    comentarios = supabase.table("comentarios").select("*").eq("produto_id", produto_id).execute().data
    if not comentarios:
        print("Nenhum comentário encontrado.")
        return

    for i, c in enumerate(comentarios):
        print(f"{i + 1}. Texto: {c['texto']} | Aprovado: {c['aprovado']}")


def remover_comentario_cliente(user_id):
    produto = input("Produto para remover comentário: ")
    response = supabase.table("produtos").select("id", "nome", "plataforma").ilike("nome", f"%{produto}%").execute()
    produtos = response.data

    if not produtos:
        print("Produto não encontrado.")
        return

    for i, p in enumerate(produtos):
        print(f"{i + 1}. {p['nome']} | Plataforma: {p['plataforma']}")
    try:
        index = int(input("\nNúmero do produto: ")) - 1
        produto_id = produtos[index]["id"]
    except:
        print("Escolha inválida.")
        return

    response_comentarios = supabase.table("comentarios").select("*").eq("produto_id", produto_id).eq("user_id", user_id).execute()
    comentarios = response_comentarios.data

    if not comentarios:
        print("Não há comentários seus neste produto.")
        return

    for i, c in enumerate(comentarios):
        print(f"{i + 1}. Texto: {c['texto']}")
    try:
        index = int(input("\nNúmero do comentário a remover: ")) - 1
        comentario_id = comentarios[index]["id"]
    except:
        print("Escolha inválida.")
        return

    if input("Confirmar remoção? (s/n): ").lower() == "s":
        supabase.table("comentarios").delete().eq("id", comentario_id).execute()
        print("Comentário removido.")
    else:
        print("Remoção cancelada.")

def remover_comentario_admin():
    produto = input("Produto para revisar comentários: ")
    response = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute()
    produtos = response.data

    if not produtos:
        print("Produto não encontrado.")
        return

    for i, p in enumerate(produtos):
        print(f"{i + 1}. {p['nome']}")
    try:
        index = int(input("\nNúmero do produto: ")) - 1
        produto_id = produtos[index]["id"]
    except:
        print("Escolha inválida.")
        return

    comentarios = supabase.table("comentarios").select("*").eq("produto_id", produto_id).execute().data
    if not comentarios:
        print("Nenhum comentário encontrado.")
        return

    for i, c in enumerate(comentarios):
        print(f"{i + 1}. ID: {c['id']} | Texto: {c['texto']} | Aprovado: {c['aprovado']}")
    try:
        index = int(input("\nNúmero do comentário a remover: ")) - 1
        comentario_id = comentarios[index]["id"]
    except:
        print("Escolha inválida.")
        return

    if input("Confirmar remoção? (s/n): ").lower() == "s":
        supabase.table("comentarios").delete().eq("id", comentario_id).execute()
        print("✅ Comentário removido pelo administrador.")
    else:
        print("Remoção cancelada.")



# 🚪 Entrada principal
user = carregar_sessao()
if not user:
    print("⛔ Precisas de fazer login para aceder ao menu de comentários.")
    sys.exit()

print(f"\n💬 Bem-vindo {user['nome']} ({user['tipo']})")

if user["tipo"] == "cliente":
    print("1 -> Fazer comentário")
    print("2 -> Remover comentário")
    escolha = int(input("Opção: "))
    if escolha == 1:
        fazer_comentario(user["id"])
    elif escolha == 2:
        remover_comentario_cliente(user["id"])
    else:
        print("Opção inválida.")
elif user["tipo"] == "admin":
    print("1 -> Listar comentários por produto")
    print("2 -> Aprovar/Rejeitar comentário")
    print("3 -> Remover comentário")
    escolha = int(input("Opção: "))
    if escolha == 1:
        listar_comentario_por_produto()
    elif escolha == 2:
        julgar_comentario()
    elif escolha == 3:
        remover_comentario_admin()
    else:
        print("Opção inválida.")
else:
    print("Tipo de utilizador desconhecido.")