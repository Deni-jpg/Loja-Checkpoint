from db import supabase
from tabulate import tabulate

def fazer_compra():
    print("Produtos disponíveis:\n")
    response = supabase.table("produtos").select('id', 'nome', 'preco', 'stock', 'plataforma').execute()

    if response.data:
        produtos = response.data
        for i, produto in enumerate(produtos, start=1):
            print(f"{i}. {produto['nome']} ({produto['plataforma']}) - €{produto['preco']:.2f} | Stock: {produto['stock']}")

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
                    print("Continuar a lógica da compra")
                elif confirmar_maiusculo == "N":
                    print("Continuar a lógica da compra")
                else:
                    print("Opção inválida!!")
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida. Digite um número.")
    else:
        print("Nenhum produto encontrado!")



fazer_compra()