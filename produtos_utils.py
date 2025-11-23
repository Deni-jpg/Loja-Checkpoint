"""
Módulo de consulta de produtos.

Este módulo permite:
- Listar todos os produtos da base de dados Supabase.
- Obter informações detalhadas de um produto específico.
- Utilizar tanto em modo visual (terminal) como em modo de dados
  para integração com outras funcionalidades.

Funções principais:
    - listar_produtos()
    - obter_produto_por_id()
"""

from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from tabulate import tabulate
from colorama import Fore, Style


def listar_produtos(modo="visual", utilizador=None):
    """Lista produtos registados na base de dados.

    Modos de operação:
        - ``visual``: mostra uma tabela formatada no terminal.
        - ``dados``: retorna a lista de produtos como dicionários
          sem qualquer output visual.

    Args:
        modo (str, optional): Define o modo de apresentação.
            Pode ser ``"visual"`` ou ``"dados"``.
            Por omissão é ``"visual"``.
        utilizador (str | None): Nome do utilizador logado,
            utilizado apenas para exibição na interface.

    Returns:
        list[dict] | None:
            - Se ``modo="dados"``, retorna uma lista de produtos no formato:
              ``{"id", "nome", "preco", "plataforma", "stock", ...}``
            - Caso contrário, não retorna valor e exibe o conteúdo no terminal.

    Nota:
        Esta função depende da base de dados Supabase para obter os produtos.
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
    """Obtém um produto específico pelo ID.

    Modos de operação:
        - ``dados``: retorna o produto como dicionário
        - ``visual``: apresenta detalhes formatados no terminal

    Args:
        produto_id (int | str): ID do produto a consultar.
        modo (str, optional): ``"dados"`` ou ``"visual"``.
        utilizador (str | None): Nome do utilizador logado
            para exibição na interface.

    Returns:
        dict | None:
            - Dicionário com os dados do produto se encontrado
            - ``None`` caso o produto não exista

    Informações apresentadas:
        - Nome
        - Plataforma
        - Preço
        - Stock
        - Descrição
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
