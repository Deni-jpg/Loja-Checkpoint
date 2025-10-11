from db import supabase
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
