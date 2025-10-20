from db import supabase
from tabulate import tabulate
import getpass
import bcrypt
from datetime import datetime

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
    
def mostrar_produtos(produtos):
    for i, produto in enumerate(produtos, start=1):
        print(f"{i}. {produto['nome']} ({produto['plataforma']}) - {produto['preco']:.2f}€ | Stock: {produto['stock']} | Vendas: {produto['vendas']}")

def procurar_produtos():
    print("\n Procurar produtos")
    print("1 -> Por nome")
    print("2 -> Por plataforma")
    print("3 -> Ver os 10 produtos mais vendidos")
    try:
        escolha = int(input("Escolha uma opção: "))
        if escolha == 1:
            nome = input("Digite o nome do jogo: ")
            response = supabase.table("produtos").select("*").ilike("nome", f"%{nome}%").execute()
        elif escolha == 2:
            plataforma = input("Digite a plataforma: ")
            response = supabase.table("produtos").select("*").ilike("plataforma", f"%{plataforma}%").execute()
        elif escolha == 3:
            response = supabase.table("produtos").select("*").order("vendas", desc=True).limit(10).execute()
        else:
            print("Opção inválida.")
            return []
        produtos = response.data
        if produtos:
            print("\nProdutos encontrados:")
            mostrar_produtos(produtos)
            return produtos
        else:
            print("Nenhum produto encontrado!!")
            return []
    except ValueError:
        print("Entrada Inválida.")
        return []
def listar_todos_produtos():
    print("\nLista de todos os produtos disponíveis:")
    response = supabase.table("produtos").select('id', 'nome', 'preco', 'stock', 'plataforma', 'vendas').execute()
    produtos = response.data
    if produtos:
        mostrar_produtos(produtos)
        return produtos
    else:
        print("Nenhum produto disponível.")
        return []

def historico_compras(user_id):
    response = supabase.table("compras").select("produto_id", "data").eq("cliente_id", user_id).execute()
    compras = response.data

    if not compras:
        print("Ainda não fez nenhuma compra.")
        return

    print("\nHistórico de compras:")
    for c in compras:
        produto_resp = supabase.table("produtos").select("nome").eq("id", c["produto_id"]).execute()
        nome = produto_resp.data[0]["nome"] if produto_resp.data else "Desconhecido"
        data_formatada = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
        print(f"Comprado em: {data_formatada}")

def confirmar_compra(user_id, produto):
    print(f"\n Produto selecionado: {produto['nome']} ({produto['plataforma']})")
    print(f" Preço: {produto['preco']:.2f}€")
    print(f" Stock disponível: {produto['stock']}")
    confirmar = input("Confirmar compra? (S/N): ").strip().upper()

    if confirmar == "S":
        if produto["stock"] > 0:
            supabase.table("produtos").update({
                "stock": produto["stock"] - 1,
                "vendas": produto["vendas"] + 1
            }).eq("id", produto["id"]).execute()

            supabase.table("compras").insert({
                "cliente_id": user_id,
                "produto_id": produto["id"],
                "data": datetime.now().isoformat()
            }).execute()

            print("Compra realizado com sucesso!")
        else:
            print("Produto sem stock disponível.")
    elif confirmar == "N":
        print("Compra cancelada.")
    else:
        print("Opção inválida.")

def fazer_compra(user_id):
    print("\n Menu de Compras")
    print("1 -> Procurar produto")
    print("2 -> Ver todos os produtos")
    try:
        escolha = int(input("Escolha uma opção: "))
        if escolha == 1:
            produtos = procurar_produtos()
        elif escolha == 2:
            produtos = listar_todos_produtos()
        else:
            print("Opção Inválida.")
            return
        
        if produtos:
            try:
                num = int(input("\nDigite o número do produto que deseja comprar: "))
                if 1 <= num <= len(produtos):
                    confirmar_compra(user_id, produtos[num - 1])
                else:
                    print("Número inválido.")
            except ValueError:
                print("Entrada inválida.")
    except ValueError:
        print("Entrada inválida.")


def listar_compras():
    print("Por fazer")

def listar_compras_por_cliente():
    print("Por fazer")

print("\nLogin necessário para aceder ao menu de compras")
print("1 -> Cliente")
print("2 -> Administrador")
try:
    tipo = int(input("Escolha o tipo de utilizador: "))
    if tipo == 1:
        user_id = fazer_login_cliente()
        print("\nMenu de Administração")
        print("1 -> Fazer compras")
        print("2 -> Ver histórico de compras")
        if user_id:
            escolha = int(input("Opção: "))
            if escolha == 1:
                fazer_compra(user_id)
            elif escolha == 2:
                historico_compras(user_id)
            else:
                print("Opção inválida!!")
    elif tipo == 2:
        admin_id = fazer_login_admin()
        if admin_id:
            print("\nMenu de Administração")
            print("1 -> Ver todas as compras")
            print("2 -> Ver compras de um cliente")
            escolha = int(input("Escolha uma opção: "))
            if escolha == 1:
                listar_compras()
            elif escolha == 2:
                listar_compras_por_cliente()
            else:
                print("Opção inválida.")
    else:
        print("Tipo de utilizador inválido.")
except ValueError:
    print("Entrada inválida.")