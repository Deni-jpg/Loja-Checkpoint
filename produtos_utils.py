from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from tabulate import tabulate
from colorama import Fore, Style

def listar_produtos(modo="visual", utilizador=None):
    """
    Lista produtos da base de dados.
    - modo="visual" → exibe tabela formatada no terminal
    - modo="dados" → retorna lista de produtos (dict)
    - utilizador → nome do utilizador logado (para mostrar Online)
    """
    animar_carregamento("A carregar produtos...")
    response = supabase.table("produtos").select("*").order("nome").execute()
    produtos = response.data or []

    # Retorna apenas dados (sem interface)
    if modo == "dados":
        return produtos

    # Exibe visualmente no terminal
    limpar_terminal()
    cabecalho("Catálogo de Produtos", utilizador=utilizador)

    if not produtos:
        print(Fore.YELLOW + "📭 Nenhum produto encontrado." + Style.RESET_ALL)
    else:
        tabela = [
            [p["id"], p["nome"], p["plataforma"], f"€{float(p['preco']):.2f}", p["stock"]]
            for p in produtos
        ]
        print(tabulate(tabela, headers=["ID", "Nome", "Plataforma", "Preço", "Stock"], tablefmt="fancy_grid"))

    rodape(utilizador=utilizador)
    input("\nENTER para voltar...")

def obter_produto_por_id(produto_id, modo="dados", utilizador=None):
    """
    Obtém um produto específico pelo ID.
    - modo="dados" → retorna o dicionário do produto
    - modo="visual" → mostra detalhes no terminal
    - utilizador → nome do utilizador logado
    """
    response = supabase.table("produtos").select("*").eq("id", produto_id).execute()
    produto = response.data[0] if response.data else None

    if not produto:
        print(Fore.RED + "❌ Produto não encontrado." + Style.RESET_ALL)
        return None

    if modo == "dados":
        return produto

    limpar_terminal()
    cabecalho(f"Detalhes do Produto #{produto_id}", utilizador=utilizador)

    print(Fore.CYAN + f"🕹️  Nome: {produto['nome']}" + Style.RESET_ALL)
    print(f"🎮 Plataforma: {produto['plataforma']}")
    print(f"💰 Preço: €{produto['preco']:.2f}")
    print(f"📦 Stock: {produto['stock']}")
    print(f"📝 Descrição: {produto['descricao'] or 'Sem descrição.'}")

    rodape(utilizador=utilizador)
    input("\nENTER para voltar...")
