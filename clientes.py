from auth import registar_utilizador, login_utilizador, logout_utilizador
from db import supabase

<<<<<<< HEAD
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
=======
def editar_perfil(user_id):
>>>>>>> d99c774b3aa72dae51d7a215259a2e616e2eb58b
    nome = input("Novo nome: ")
    supabase.table("perfil").update({
        "nome": nome
    }).eq("user_id", user_id).execute()
    print("Perfil editado com sucesso.")

<<<<<<< HEAD
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
    response = supabase.table("clientes").select('id', 'nome', 'email', 'criado_em').execute()

    if response.data:
        clientes = response.data
        for i, cliente in enumerate(clientes, start=1):
            print(f"{i}. Nome: {cliente['nome']} - Email: {cliente['email']} - criado em: {cliente['criado_em']}")
=======
def remover_perfil(user_id):
    supabase.table("perfil").delete().eq("user_id", user_id).execute()
    print("Perfil removido com sucesso.")

def listar_utilizadores():
    response = supabase.table("perfil").select('user_id', 'nome', 'tipo').execute()
    if response.data:
        for i, perfil in enumerate(response.data, start=1):
            print(f"{i}. Nome: {perfil['nome']} - Tipo: {perfil['tipo']}")
>>>>>>> d99c774b3aa72dae51d7a215259a2e616e2eb58b

def criar_admin():
    nome = input("Nome do admin: ")
    email = input("Email: ")
    password = input("Password: ")
    registar_utilizador(email, password, nome, "admin")


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
        nome = input("Nome: ")
        email = input("Email: ")
        password = input("Password: ")
        registar_utilizador(email, password, nome, "cliente")
    elif funcao == 2:
<<<<<<< HEAD
        login_cliente()
=======
        email = input("Email: ")
        password = input("Password: ")
        user = login_utilizador(email, password)
        if user:
            print(f"Bem-vindo, {email}")
        else:
            print("Credenciais inválidas.")
>>>>>>> d99c774b3aa72dae51d7a215259a2e616e2eb58b

elif tipo == 2:
    print("\nLogin Administrador")
    email = input("Email: ")
    password = input("Password: ")
    user = login_utilizador(email, password)

    if user:
        perfil = supabase.table("perfil").select("tipo").eq("user_id", user.id).execute()
        if perfil.data and perfil.data[0]["tipo"] == "admin":
            print("\n Acesso autorizado ao menu de administração.")
            print("1 -> Listar utilizadores")
            print("2 -> Editar perfil")
            print("3 -> Remover perfil")
            funcao = int(input("Escolha a função: "))
            if funcao == 1:
                listar_utilizadores()
            elif funcao == 2:
                editar_perfil(user.id)
            elif funcao == 3:
                remover_perfil(user.id)
        else:
            print("Acesso negado. Não és administrador.")
    else:
        print("Credenciais inválidas.")

