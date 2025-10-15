from db import supabase

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
    
def listar_produtos():
    response = supabase.table("produtos").select("*").execute()
    if response.data:
        produtos = response.data
        for i, produto in enumerate(produtos, start=1):
            print(f"{i}. {produto['nome']} ({produto['plataforma']}) - {produto['preco']:.2f}€ | Stock: {produto['stock']}")

print("Funções: ")
print("1 -> Adicionar produtos")
print("2 -> Listar produtos")
print("3 -> Editar produtos")
print("4 -> Deletar produtos")
print("5 -> Listar produtos que precisam ser repostos")
print("6 -> Listar os 3 produtos mais vendidos")
funcao = int(input("Que função quer fazer na tabela produtos(insira o número): "))
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