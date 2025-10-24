from db import supabase
import json
import sys

from produtos_utils import listar_produtos, obter_produto_por_id

def carregar_sessao():
    try:
        with open("sessao.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def adicionar_produto():
    nome = input("Nome: ")
    plataforma = input("Plataforma: ")
    preco = float(input("Preço: "))
    stock = int(input("Stock: "))
    descricao = input("Descrição: ")
    supabase.table("produtos").insert({
        "nome" : nome,
        "plataforma" : plataforma,
        "preco" : preco,
        "stock" : stock,
        "descricao" : descricao
    }).execute()
    print("Produto adicionado")

def atualizar_produto():
    produto_id = int(input("Qual o ID do produto: "))
    nome = input("Novo nome: ")
    plataforma = input("Nova plataforma: ")
    preco = float(input("Novo preço: "))
    stock = int(input("Novo stock: "))
    descricao = input("Nova descrição: ")
    supabase.table("produtos").update({
        "nome" : nome,
        "plataforma" : plataforma,
        "preco" : preco,
        "stock" : stock,
        "descricao" : descricao
    }).eq("id", produto_id).execute()
    print("Produto atualizado")

def listar_produtos_com_stock_baixo():
    response = (
    supabase.table("produtos").select('nome','stock').lt('stock',3).execute()
    )
    if response.data:
        for produto in response.data:
            print(produto)

def lista_produtos_mais_vendidos():
    response = (
        supabase.table("produtos").select('nome','vendas').limit(3).order('vendas', desc=True).execute()
    )
    if response.data:
        for produto in response.data:
            print(produto)

def remover_produto():
    produto_id = int(input("Qual o ID do produto: "))
    response = (
        supabase.table("produtos")
        .delete()
        .eq("id", produto_id)
        .execute()
    )
    print("Produto removido com sucesso.")
    
 
user = carregar_sessao()
if not user or user["tipo"] != "admin":
    print("⛔ Acesso restrito. Apenas administradores podem gerir produtos.")
    sys.exit()

print(f"\n✅ Bem-vindo {user['nome']} ao menu de administração de produtos.")

print("\nFunções disponíveis:")
print("1 -> Adicionar produto")
print("2 -> Listar produtos")
print("3 -> Editar produto")
print("4 -> Remover produto")
print("5 -> Listar produtos com stock baixo")
print("6 -> Listar os 3 produtos mais vendidos")

try:
    funcao = int(input("Escolha a função (número): "))
    match funcao:
        case 1:
            adicionar_produto()
        case 2:
            listar_produtos()
        case 3:
            atualizar_produto()
        case 4:
            remover_produto()
        case 5:
            listar_produtos_com_stock_baixo()
        case 6:
            lista_produtos_mais_vendidos()
        case _:
            print("Opção inválida.")
except ValueError:
    print("Entrada inválida.")