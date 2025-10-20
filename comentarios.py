from db import supabase
import getpass
import bcrypt
from main import cliente_logado, TEXTS, THEME_COLORS, color, load_config

config = load_config()
theme = config["theme"]

#if not cliente_logado:
#    print("⚠️  Você precisa estar logado para acessar esta seção.")
#    input(color(f"{TEXTS['back']}", THEME_COLORS[theme]["prompt"]))
#    exit()

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
        print("Login bem-sucedido, pode continuar para o menu de comentários.")
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
    response_cliente = supabase.table("clientes").select("id").eq("id", user_id).execute()
    autor = response_cliente.data[0]
    produto = input("\nQual o produto que quer fazer o comentário: ")
    response = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute()
    produtos = response.data

    if not produtos:
        print("Produto não encontrado.")
        return

    # Se houver mais de um produto, mostrar opções
    if len(produtos) > 1:
        print("\nProdutos encontrados:")
        for i, p in enumerate(produtos):
            print(f"{i + 1}. {p['nome']}")

        escolha = input("\nDigite o número do produto desejado: ")
        try:
            index = int(escolha) - 1
            produto_id = produtos[index]["id"]
        except (ValueError, IndexError):
            print("Escolha inválida.")
            return
    else:
        produto_id = produtos[0]["id"]
    texto = input("\nEscreva o seu comentário: ")

    supabase.table("comentarios").insert({
        "cliente_id": autor["id"],
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
    produto = input("Indique o produto que quer ver o comentário: ")
    response = supabase.table("produtos").select("nome, id").ilike("nome", f"%{produto}%").execute()
    produtos = response.data

    if not produtos:
        print("Produto não encontrado.")
        return

    print("\nProdutos encontrados:")
    for i, p in enumerate(produtos):
        print(f"{i + 1}. {p['nome']} ID -> {p['id']}")

    escolha = input("\nDigite o número do produto desejado: ")
    try:
        index = int(escolha) - 1
        produto_id = produtos[index]["id"]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    # Corrigido: usar eq em vez de ilike
    response_comentarios = supabase.table("comentarios").select("*").eq("produto_id", produto_id).execute()
    comentarios = response_comentarios.data

    if not comentarios:
        print("Nenhum comentário encontrado para este produto.")
        return

    print("\nComentários encontrados:")
    for i, c in enumerate(comentarios):
        print(f"{i + 1}. ID do comentário: {c['id']} | Produto ID: {c['produto_id']} | Autor: {c['autor']} | Texto: {c['texto']} | Aprovado: {c['aprovado']}")



def remover_comentario_cliente(user_id):
    # Verifica se o cliente existe
    response_cliente = supabase.table("clientes").select("id").eq("id", user_id).execute()
    if not response_cliente.data:
        print("Cliente não encontrado.")
        return
    cliente_id = response_cliente.data[0]["id"]

    produto = input("Indique o produto que quer remover o comentário: ")
    response = supabase.table("produtos").select("nome, id, plataforma").ilike("nome", f"%{produto}%").execute()
    produtos = response.data

    if not produtos:
        print("Produto não encontrado.")
        return

    print("\nProdutos encontrados:")
    for i, p in enumerate(produtos):
        print(f"{i + 1}. {p['nome']} | Plataforma: {p['plataforma']}")

    escolha = input("\nDigite o número do produto desejado: ")
    try:
        index = int(escolha) - 1
        produto_id = produtos[index]["id"]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    #Dar fetch dos comentários do produto feitos pelo cliente autenticado
    response_comentarios = supabase.table("comentarios").select("*").eq("produto_id", produto_id).eq("cliente_id", cliente_id).execute()
    comentarios = response_comentarios.data

    if not comentarios:
        print("Não há comentários seus neste produto.")
        return

    print("\nSeus comentários encontrados:")
    for i, c in enumerate(comentarios):
        print(f"{i + 1}. Texto: {c['texto']}")

    escolha_comentario = input("\nDigite o número do comentário que deseja remover: ")
    try:
        index = int(escolha_comentario) - 1
        comentario_id = comentarios[index]["id"]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    confirmacao = input("Tem certeza que deseja remover este comentário? (s/n): ").lower()
    if confirmacao != "s":
        print("Remoção cancelada.")
        return

    supabase.table("comentarios").delete().eq("id", comentario_id).execute()
    print("Comentário removido com sucesso!")

def remover_comentario_admin():
    produto = input("Indique o produto que quer revisar os comentários: ")
    response = supabase.table("produtos").select("nome, id").ilike("nome", f"%{produto}%").execute()
    produtos = response.data

    if not produtos:
        print("Produto não encontrado.")
        return

    print("\nProdutos encontrados:")
    for i, p in enumerate(produtos):
        print(f"{i + 1}. {p['nome']} ID -> {p['id']}")

    escolha = input("\nDigite o número do produto desejado: ")
    try:
        index = int(escolha) - 1
        produto_id = produtos[index]["id"]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    # Dar fetch de todos os comentários do produto
    response_comentarios = supabase.table("comentarios").select("*").eq("produto_id", produto_id).execute()
    comentarios = response_comentarios.data

    if not comentarios:
        print("Nenhum comentário encontrado para este produto.")
        return

    print("\nComentários encontrados:")
    for i, c in enumerate(comentarios):
        print(f"{i + 1}. ID do comentário: {c['id']} | Cliente ID: {c['cliente_id']} | Texto: {c['texto']} | Aprovado: {c['aprovado']}")

    escolha_comentario = input("\nDigite o número do comentário que deseja remover: ")
    try:
        index = int(escolha_comentario) - 1
        comentario_id = comentarios[index]["id"]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    confirmacao = input("Tem certeza que deseja remover este comentário? (s/n): ").lower()
    if confirmacao != "s":
        print("Remoção cancelada.")
        return

    supabase.table("comentarios").delete().eq("id", comentario_id).execute()
    print("Comentário removido com sucesso pelo administrador.")



print("Fazer login para aceder o menu comentários: \n")

print("Escolha o tipo de utilizador:")
print("1 -> Cliente")
print("2 -> Administrador")
tipo = int(input("Opção: "))

if tipo == 1:
    user_id = fazer_login_cliente()
    if user_id:
        print("Que tipo de ação vai fazer: \n")
        print("1 -> Fazer um comentário.")
        print("2 -> Remover um comentário.")
        escolha = int(input("Opção:"))
        if escolha == 1:
            fazer_comentario(user_id)
        elif escolha == 2:
            remover_comentario_cliente(user_id)
elif tipo == 2:
    admin_id = fazer_login_admin()
    if admin_id:
        print("Que tipo de ação vai fazer: \n")
        print("1 -> Listagem de comentários por produtos.")
        print("2 -> Aprovar/Rejeitar comentário.")
        print("3 -> Remover Comentário.")
        print("4 -> Listar comentários por produto.")
        escolha = int(input("Opção: "))
        if escolha == 1:
            listar_comentario_por_produto()
        elif escolha == 2:
            julgar_comentario()
        elif escolha == 3:
            remover_comentario_admin()
        elif escolha == 4:
            listar_comentario_por_produto()
        else:
            print("Opção inválida!!")
else: 
    print("Opção inválida!!")
