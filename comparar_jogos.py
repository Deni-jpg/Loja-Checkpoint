"""
Módulo para comparar jogos disponíveis na loja.

Este módulo permite:
- Carregar a sessão do utilizador a partir de um ficheiro JSON.
- Listar e escolher jogos da base de dados (Supabase).
- Comparar múltiplos jogos em termos de preço, plataforma e avaliação média.
- Apresentar os resultados numa tabela formatada no terminal.
"""

from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from tabulate import tabulate
import json, sys


def carregar_sessao():
    """Carrega a sessão do utilizador a partir do ficheiro ``sessao.json``.

    Tenta abrir o ficheiro ``sessao.json`` no diretório atual e ler
    os dados de sessão em formato JSON. Caso o ficheiro não exista
    ou ocorra algum erro na leitura/parse, devolve ``None``.

    Returns:
        dict | None: Dicionário com os dados da sessão
        (por exemplo, ``{"id": ..., "nome": ...}``) ou ``None``
        se não for possível carregar a sessão.
    """
    try:
        with open("sessao.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def escolher_jogo(excluir_ids=None):
    """Permite ao utilizador escolher um jogo da lista de produtos.

    É possível:
    - Filtrar jogos pelo nome (pesquisa parcial).
    - Excluir certos IDs de produtos (por exemplo, já selecionados).

    Os jogos são carregados da tabela ``produtos`` da base de dados
    e apresentados numa tabela com:
    número, nome, plataforma e preço. O utilizador escolhe pelo número.

    Args:
        excluir_ids (list[int | str] | None): Lista de IDs de produtos
            que devem ser excluídos da listagem. Útil para evitar que
            o mesmo jogo seja escolhido mais do que uma vez. Se for
            ``None``, não é aplicado filtro de exclusão.

    Returns:
        dict | None: Dicionário do produto selecionado (com as chaves
        ``"id"``, ``"nome"``, ``"preco"``, ``"plataforma"``), ou
        ``None`` se não houver jogos disponíveis ou se a escolha for inválida.
    """
    termo = input("\n🔍 Nome do jogo (ou ENTER para listar todos): ").strip()

    query = supabase.table("produtos").select("id, nome, preco, plataforma")
    if termo:
        query = query.ilike("nome", f"%{termo}%")
    if excluir_ids:
        query = query.not_.in_("id", excluir_ids)

    animar_carregamento("A carregar jogos...")
    produtos = query.execute().data or []
    if not produtos:
        print("❌ Nenhum jogo encontrado.")
        return None

    tabela = [[i + 1, p["nome"], p["plataforma"], f"€{float(p['preco']):.2f}"] for i, p in enumerate(produtos)]
    print(tabulate(tabela, headers=["Nº", "Nome", "Plataforma", "Preço"], tablefmt="fancy_grid"))

    try:
        idx = int(input("\nEscolha o número do jogo: ")) - 1
        return produtos[idx]
    except:
        print("⚠️ Escolha inválida.")
        return None


def comparar_jogos():
    """Executa o fluxo de comparação de jogos na interface de terminal.

    Passos principais:
        1. Verifica se existe sessão do utilizador (login obrigatório).
        2. Pede ao utilizador para escolher pelo menos dois jogos.
        3. Opcionalmente permite adicionar mais jogos à comparação.
        4. Para cada jogo selecionado, calcula a avaliação média
           com base na tabela ``avaliacoes`` (campo ``estrelas``).
        5. Mostra uma tabela comparativa com:
           - Nome
           - Preço
           - Plataforma
           - Avaliação média (ou "Sem avaliações")

    A função é interativa (usa inputs e prints) e não devolve valor.

    Raises:
        SystemExit: Se não existir sessão válida, o programa termina
        com uma mensagem a indicar que é necessário login.
    """
    sessao = carregar_sessao()
    if not sessao:
        print("⛔ Precisas de fazer login para comparar jogos.")
        sys.exit()

    nome = sessao["nome"]
    limpar_terminal()
    cabecalho("Comparar Jogos", utilizador=nome)

    print(Fore.MAGENTA + "\n🎮 Comparador de Jogos" + Style.RESET_ALL)
    print("-" * 50)

    jogo1 = escolher_jogo()
    if not jogo1:
        return
    jogo2 = escolher_jogo(excluir_ids=[jogo1["id"]])
    if not jogo2:
        return

    selecionados = [jogo1, jogo2]
    while True:
        extra = input("➕ Adicionar outro jogo? (s/n): ").lower().strip()
        if extra == "s":
            novo = escolher_jogo(excluir_ids=[p["id"] for p in selecionados])
            if novo:
                selecionados.append(novo)
        else:
            break

    animar_carregamento("A gerar comparação...")

    for p in selecionados:
        avals = supabase.table("avaliacoes").select("estrelas").eq("produto_id", p["id"]).execute().data or []
        if avals:
            media = sum(a["estrelas"] for a in avals) / len(avals)
            p["avaliacao"] = f"{media:.1f} ⭐"
        else:
            p["avaliacao"] = "Sem avaliações"

    tabela = [[p["nome"], f"€{p['preco']:.2f}", p["plataforma"], p["avaliacao"]] for p in selecionados]
    print("\n🆚 Comparação de Jogos:\n")
    print(tabulate(tabela, headers=["Nome", "Preço", "Plataforma", "Avaliação Média"], tablefmt="fancy_grid"))

    rodape(utilizador=nome)
    input("\nENTER para voltar...")


if __name__ == "__main__":
    comparar_jogos()
