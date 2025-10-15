import bcrypt
import getpass
from db import supabase

def registar_cliente():
    nome = input("Nome: ")
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    existe = supabase.table("clientes").select("id").eq("email", email).execute()
    if existe.data:
        print("Já existe um utilizador com este email.")
        return None

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    res = supabase.table("clientes").insert({
        "nome": nome,
        "email": email,
        "password": hashed_password
    }).execute()

    print("Cliente registado com sucesso.")
    return res.data[0]


def login_cliente():
    email = input("Email do utilizador: ")
    password = getpass.getpass("Password: ")

    res = supabase.table("clientes").select("id", "password").eq("email", email).execute()
    if not res.data:
        print("Cliente não encontrado.")
        return None

    user = res.data[0]
    hashed = user["password"]

    if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
        print("Login bem-sucedido.")
        return user["id"]
    else:
        print("Password incorreta.")
        return None

def editar_cliente(cliente_id):
    nome = input("Novo nome: ")
    password = getpass.getpass("Nova password: ")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    supabase.table("clientes").update({
        "nome": nome,
        "password": hashed
    }).eq("id", cliente_id).execute()
    print("Cliente editado com sucesso.")

def remover_cliente(cliente_id):
    cliente_id = input("Digite o id do cliente: ")
    response = (
        supabase.table("clientes")
        .delete()
        .eq("id", cliente_id)
        .execute() 
    )
    print("Cliente removido com sucesso.")

def listar_clientes():
    response = (
        supabase.table("clientes")
        .select("*")
        .execute()
    )
    print("Clientes listados:", response)

def criar_admin():
    nome = input("Nome do admin: ")
    email = input("Email do admin: ")
    password = getpass.getpass("Password: ")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    supabase.table("admins").insert({
        "email": email,
        "nome": nome,
        "password": hashed
    }).execute()
    print("Administrador criado com sucesso.")

def login_admin():
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

# Menu principal
print("Escolha o tipo de utilizador:")
print("1 -> Cliente")
print("2 -> Administrador")
tipo = int(input("Opção: "))

if tipo == 1:
    print("\nMenu Cliente")
    print("1 -> Registar")
    print("2 -> Fazer Login")
    funcao = int(input("Escolha a função: "))
    if funcao == 1:
        registar_cliente()
    elif funcao == 2:
        login_cliente()

elif tipo == 2:
    admin_id = login_admin()
    if admin_id:
        print("\n✅ Acesso autorizado ao menu de administração.")
        print("1 -> Listar clientes")
        print("2 -> Editar cliente")
        print("3 -> Remover cliente")
        funcao = int(input("Escolha a função: "))
        if funcao == 1:
            listar_clientes()
        elif funcao == 2:
            cliente_id = int(input("ID do cliente a editar: "))
            editar_cliente(cliente_id)
        elif funcao == 3:
            cliente_id = int(input("ID do cliente a remover: "))
            remover_cliente(cliente_id)
    else:
        print("⛔ Acesso negado. Credenciais inválidas.")


