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

#def listar_produtos():
     

print("Funções: ")
print("1 -> Adicionar produtos")
print("2 -> Listar produtos")
funcao = int(input("Que função quer fazer na tabela produtos(insira o número): "))
match funcao:
        case 1:
            adicionar_produto()