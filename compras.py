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

def fazer_compra(user_id):

    escolha2 = int(input("\nPrefere pesquisar o nome/plataforma do jogo ou ver todos os produtos disponíveis e selecionar através desse menu? (1 -> pesquisar; 2 -> ver lista produtos) \n"))
    if escolha2 == 1:
        print(" -- Menu Procurar -- ")
        escolha3 = int(input("\nProcurar por nome ou plataforma? (1 --> nome, 2 --> plataforma)"))
        if escolha3 == 1:
            nome_jogo = input("Insira o nome do jogo: ")
            response = supabase.table("produtos").select("*").ilike("nome", f"%{nome_jogo}%").execute()
            print("\nJogos: ", "\n")
            if response.data:
                produtos = response.data
                for i, produto in enumerate(produtos, start=1):
                    print(f"{i}. {produto['nome']} ({produto['plataforma']}) - {produto['preco']:.2f}€ | Stock: {produto['stock']}")
            else:
                print("Jogo não encontrado!!")
        elif escolha3 == 2:
            plataforma_jogo = input("Insira a plataforma: ")
            response = supabase.table("produtos").select("*").ilike("plataforma",f"%{plataforma_jogo}%").execute()
            print("\nJogos da plataforma: ", plataforma_jogo, "\n")
            if response.data:
                produtos = response.data
                for i, produto in enumerate(produtos, start=1):
                    print(f"{i}. {produto['nome']} ({produto['plataforma']}) - {produto['preco']:.2f}€ | Stock: {produto['stock']}")
            else:
                print("Nenhum jogo encontrado nessa plataforma!!")
    elif escolha2 == 2:    
        print("Produtos disponíveis:\n")
        response = supabase.table("produtos").select('id', 'nome', 'preco', 'stock', 'plataforma', 'vendas').execute()

        if response.data:
            produtos = response.data
            for i, produto in enumerate(produtos, start=1):
                print(f"{i}. {produto['nome']} ({produto['plataforma']}) - {produto['preco']:.2f}€ | Stock: {produto['stock']}")

            # Escolha do utilizador
            escolha = input("\nDigite o número do produto que deseja comprar: ")
            try:
                escolha = int(escolha)
                if 1 <= escolha <= len(produtos):
                    produto_escolhido = produtos[escolha - 1]
                    print(f"\nNome: {produto_escolhido['nome']} ({produto_escolhido['plataforma']})")
                    print(f"Preço: €{produto_escolhido['preco']:.2f}")
                    print(f"Stock disponível: {produto_escolhido['stock']}")
                    #Confirmar
                    confirmar = input("\nTem certeza(S/N): ")
                    confirmar_maiusculo = confirmar.upper()
                    if confirmar_maiusculo == "S":
                        print("Opção escolhida: ", confirmar_maiusculo)
                        if produto_escolhido["stock"] > 0:
                            novo_stock = produto_escolhido["stock"] - 1
                            vendas_novas = produto_escolhido["vendas"] + 1
                            supabase.table("produtos").update({
                                "stock": novo_stock,
                                "vendas": vendas_novas
                            }).eq("id", produto_escolhido["id"]).execute()

                            supabase.table("compras").insert({
                                "cliente_id": user_id,
                                "produto_id": produto_escolhido["id"],
                                "data": datetime.now().isoformat()
                            }).execute()

                            print("\nCompra feita com sucesso!!")

                        else:
                            print("Produto sem stock disponível.")

                    elif confirmar_maiusculo == "N":
                        print("Opção escolhida", confirmar_maiusculo)
                        print("\nCompra cancelada")
                    else:
                        print("Opção inválida!!")
                else:
                    print("Número inválido.")
            except ValueError:
                print("Entrada inválida. Digite um número.")
        else:
            print("Nenhum produto encontrado!")
    else: 
        print("\nOpção Inválida")

def listar_compras():
    print("Por fazer")

def listar_compras_por_cliente():
    print("Por fazer")

print("Fazer login para aceder o menu compras: \n")

print("Escolha o tipo de utilizador:")
print("1 -> Cliente")
print("2 -> Administrador")
tipo = int(input("Opção: "))

if tipo == 1:
    user_id = fazer_login_cliente()
    if user_id:
        fazer_compra(user_id)
elif tipo == 2:
    admin_id = fazer_login_admin()
    if admin_id:
        print("Que tipo de listagem vai fazer: \n")
        print("1 -> Listagem de todas as compras")
        print("2 -> Listagem de compras de um x cliente")
        escolha = int(input("Opção: "))
        if escolha == 1:
            listar_compras()
        elif escolha == 2:
            listar_compras_por_cliente()
        else:
            print("Opção inválida!!")
else: 
    print("Opção inválida!!")