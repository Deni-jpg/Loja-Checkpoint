from db import supabase
<<<<<<< HEAD
import getpass
import bcrypt

def fazer_login_cliente():
    email = input("Email utilizador: ")
    password = getpass.getpass("Password: ")

    res = supabase.table("clientes").select("id", "password").eq("email", email).execute()
    if not res.data:
        print("Cliente não encontrado.")
        return None

    user = res.data[0]
    hashed = user["password"]

    if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
        print("Login bem-sucedido, pode continuar para o menu de compras.")
        return user["id"]
    else:
        print("Password incorreta.")
        return None  
    
def fazer_login_admin():
    email = input("Email do admin: ")
    password = getpass.getpass("Password: ")

    res = supabase.table("admins").select("id", "password").eq("email", email).execute()
    if not res.data:
        print("Admin não encontrado.")
        return None

    admin = res.data[0]
    hashed = admin["password"]

    if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
        print("Login bem-sucedido.")
        return admin["id"]
    else:
        print("Password incorreta.")
        return None


def fazer_comentario(user_id):
    autor = input("Digite seu nome: ")
    texto = input("\nEscreva seu comentário: ")

    supabase.table("comentarios").insert({
        "autor": autor,
        "texto": texto
    }).execute()
    print("Por fazer")

def julgar_comentario():
    print("Por fazer")

def listar_comentario_por_produto():
    print("Por fazer")

def remover_comentario():
    print("Por fazer")

print("Fazer login para aceder o menu comentários: \n")

print("Escolha o tipo de utilizador:")
print("1 -> Cliente")
print("2 -> Administrador")
tipo = int(input("Opção: "))

if tipo == 1:
    user_id = fazer_login_cliente()
    if user_id:
        fazer_comentario(user_id)
elif tipo == 2:
    admin_id = fazer_login_admin()
    if admin_id:
        print("Que tipo de ação vai fazer: \n")
        print("1 -> Listagem de comentários por produtos.")
        print("2 -> Aprovar/Rejeitar comentário.")
        print("3 -> Remover Comentário.")
        escolha = int(input("Opção: "))
        if escolha == 1:
            listar_comentario_por_produto()
        elif escolha == 2:
            julgar_comentario()
        elif escolha == 3:
            remover_comentario()
        else:
            print("Opção inválida!!")
else: 
    print("Opção inválida!!")
=======
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
>>>>>>> d99c774b3aa72dae51d7a215259a2e616e2eb58b
