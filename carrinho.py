"""
Módulo de gestão do carrinho de compras.

Este módulo trata de:
- Gestão da sessão do utilizador ligada ao carrinho.
- Criação e recuperação de carrinhos ativos.
- Adição, remoção e listagem de itens no carrinho.
- Cálculo do total do carrinho.
- Registo de compras concluídas na base de dados.
- Exibição de histórico simples e detalhado de compras.
- Interface de linha de comando para interação com o carrinho.
"""

from datetime import datetime
from notificacao_email import enviar_email
from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from tabulate import tabulate
from pathlib import Path
import json
import time

SESSAO_PATH = Path(__file__).parent / "sessao.json"


# === Sessão ===
def carregar_sessao():
    """Carrega a sessão do utilizador a partir do ficheiro JSON.

    O ficheiro de sessão é definido pela constante ``SESSAO_PATH``.
    Caso o ficheiro não exista ou ocorra algum erro na leitura/parse,
    a função devolve ``None``.

    Returns:
        dict | None: Dicionário com os dados da sessão
        (por exemplo, ``{"id": ..., "nome": ...}``) ou ``None``
        se não for possível carregar a sessão.
    """
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# === Notificação colorida ===
def notificar(msg, tipo="info"):
    """Mostra uma mensagem colorida no terminal.

    A cor é escolhida com base no tipo de notificação:
    ``info``, ``sucesso``, ``erro`` ou ``alerta``.

    Args:
        msg (str): Texto da mensagem a apresentar.
        tipo (str, optional): Tipo de mensagem. Pode ser
            ``"info"``, ``"sucesso"``, ``"erro"`` ou ``"alerta"``.
            Por omissão é ``"info"``.
    """
    cores = {
        "info": Fore.CYAN,
        "sucesso": Fore.GREEN,
        "erro": Fore.RED,
        "alerta": Fore.YELLOW
    }
    print(f"{cores.get(tipo, Fore.WHITE)}🔔 {msg}{Style.RESET_ALL}")


# === Carrinho base ===
def obter_ou_criar_carrinho(user_id):
    """Obtém o carrinho ativo do utilizador ou cria um novo.

    Procura um registo na tabela ``carrinhos`` com o campo
    ``ativo = True`` para o ``user_id`` fornecido. Se existir,
    devolve o ``id`` desse carrinho. Caso contrário, cria um
    novo carrinho ativo para o utilizador.

    Args:
        user_id (str | int): Identificador do utilizador
            na base de dados.

    Returns:
        int | str: ID do carrinho ativo associado ao utilizador.
    """
    animar_carregamento("A verificar carrinho ativo...")
    resp = (
        supabase.table("carrinhos")
        .select("id")
        .eq("user_id", user_id)
        .eq("ativo", True)
        .execute()
    )
    if resp.data:
        return resp.data[0]["id"]

    novo = supabase.table("carrinhos").insert({"user_id": user_id, "ativo": True}).execute()
    return novo.data[0]["id"]


def adicionar_item(carrinho_id, produto_id, quantidade, preco_unitario):
    """Adiciona um item ao carrinho na base de dados.

    Cria um registo na tabela ``itens_carrinho`` com a quantidade,
    preço unitário e referência ao carrinho e produto.

    Args:
        carrinho_id (int | str): ID do carrinho ao qual o item
            será associado.
        produto_id (int | str): ID do produto a adicionar.
        quantidade (int): Quantidade do produto.
        preco_unitario (float): Preço unitário do produto no momento
            da adição ao carrinho.
    """
    supabase.table("itens_carrinho").insert({
        "carrinho_id": carrinho_id,
        "produto_id": produto_id,
        "quantidade": quantidade,
        "preco_unitario": preco_unitario
    }).execute()


def listar_itens(carrinho_id):
    """Lista os itens atuais de um carrinho.

    Busca os itens na tabela ``itens_carrinho`` e, para cada item,
    consulta os dados do produto na tabela ``produtos`` (nome).
    Calcula também o total de cada linha (quantidade * preço unitário).

    Args:
        carrinho_id (int | str): ID do carrinho cujos itens
            devem ser listados.

    Returns:
        list[dict]: Lista de dicionários com as chaves:
            - ``nome`` (str): Nome do produto.
            - ``quantidade`` (int): Quantidade do produto.
            - ``preco_unitario`` (float): Preço unitário.
            - ``total`` (float): Total da linha (quantidade * preço_unitário).
    """
    animar_carregamento("A carregar itens do carrinho...")
    resp = (
        supabase.table("itens_carrinho")
        .select("produto_id, quantidade, preco_unitario")
        .eq("carrinho_id", carrinho_id)
        .execute()
    )
    itens = resp.data or []
    lista = []
    for item in itens:
        produto_resp = supabase.table("produtos").select("nome").eq("id", item["produto_id"]).execute()
        nome = produto_resp.data[0]["nome"] if produto_resp.data else "Desconhecido"
        lista.append({
            "nome": nome,
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
            "total": item["quantidade"] * item["preco_unitario"]
        })
    return lista


def remover_item(carrinho_id, produto_id):
    """Remove um item específico do carrinho.

    Apaga da tabela ``itens_carrinho`` o registo que corresponde
    ao par (carrinho_id, produto_id).

    Args:
        carrinho_id (int | str): ID do carrinho.
        produto_id (int | str): ID do produto a remover do carrinho.
    """
    supabase.table("itens_carrinho").delete().eq("carrinho_id", carrinho_id).eq("produto_id", produto_id).execute()


def calcular_total(carrinho_id):
    """Calcula o valor total de um carrinho.

    Soma ``quantidade * preco_unitario`` de todos os itens
    na tabela ``itens_carrinho`` associados ao carrinho.

    Args:
        carrinho_id (int | str): ID do carrinho.

    Returns:
        float: Valor total do carrinho. Se não existirem itens,
        devolve 0.
    """
    resp = supabase.table("itens_carrinho").select("quantidade, preco_unitario").eq("carrinho_id", carrinho_id).execute()
    return sum(item["quantidade"] * item["preco_unitario"] for item in (resp.data or []))


def finalizar_carrinho(carrinho_id, user_id):
    """Finaliza a compra do carrinho atual.

    - Obtém todos os itens do carrinho.
    - Regista cada unidade comprada na tabela ``compras``.
    - Calcula o total da compra.
    - Gera uma tabela de resumo (HTML e terminal).
    - Marca o carrinho como inativo (``ativo = False``).

    Mostra no terminal um resumo da compra, incluindo lista
    de produtos, total pago e data/hora da compra.

    Args:
        carrinho_id (int | str): ID do carrinho a finalizar.
        user_id (int | str): ID do utilizador que está a comprar.

    Returns:
        None: A função atua sobre a base de dados e o terminal,
        não devolvendo valor.
    """
    # Obtém os itens do carrinho
    resp = supabase.table("itens_carrinho").select("produto_id, quantidade").eq("carrinho_id", carrinho_id).execute()
    itens = resp.data or []
    if not itens:
        notificar("❌ O carrinho está vazio.", "erro")
        return

    animar_carregamento("A finalizar compra...")

    # Carrega dados do utilizador (apenas perfil)
    perfil_resp = supabase.table("perfil").select("nome").eq("user_id", user_id).execute()
    nome = perfil_resp.data[0]["nome"] if perfil_resp.data else "Utilizador"

    # Monta tabela HTML dos produtos (mesmo que não envies por email)
    tabela_html = ""
    total = 0

    for item in itens:
        prod_resp = supabase.table("produtos").select("nome, preco, plataforma").eq("id", item["produto_id"]).execute()
        if not prod_resp.data:
            continue

        p = prod_resp.data[0]
        subtotal = p["preco"] * item["quantidade"]
        total += subtotal

        # insere compra individual
        for _ in range(item["quantidade"]):
            supabase.table("compras").insert({
                "user_id": user_id,
                "produto_id": item["produto_id"],
                "data": datetime.now().isoformat()
            }).execute()

        tabela_html += f"""
            <tr style="text-align:center;">
                <td>{p['nome']}</td>
                <td>{p['plataforma']}</td>
                <td>{item['quantidade']}</td>
                <td>€{p['preco']:.2f}</td>
                <td>€{subtotal:.2f}</td>
            </tr>
        """

    # Fecha o carrinho
    supabase.table("carrinhos").update({"ativo": False}).eq("id", carrinho_id).execute()

    # Mostra resumo no terminal
    limpar_terminal()
    cabecalho("Compra Finalizada", utilizador=nome)
    print(Fore.GREEN + "✅ Compra finalizada com sucesso!\n" + Style.RESET_ALL)

    print(tabulate(
        [
            [p["nome"], p["plataforma"], item["quantidade"], f"€{p['preco']:.2f}", f"€{p['preco'] * item['quantidade']:.2f}"]
            for item in itens
            for p in supabase.table("produtos").select("nome, plataforma, preco").eq("id", item["produto_id"]).execute().data
        ],
        headers=["Produto", "Plataforma", "Qtd", "Preço Unit.", "Total"],
        tablefmt="fancy_grid"
    ))

    print(f"\n💰 Total pago: {Fore.YELLOW}€{total:.2f}{Style.RESET_ALL}")
    print(f"🕒 Data da compra: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    rodape(utilizador=nome)
    notificar("🛒 Compra registada na tua conta!", "sucesso")


# === Histórico de compras ===
def historico_compras(user_id, nome):
    """Mostra o histórico simples de compras do utilizador.

    Lista cada compra individual (uma linha por entrada na tabela
    ``compras``), com o produto, plataforma, preço e data/hora.

    A informação é mostrada no terminal numa tabela formatada.

    Args:
        user_id (int | str): ID do utilizador na base de dados.
        nome (str): Nome do utilizador para exibição na UI.
    """
    limpar_terminal()
    cabecalho("Histórico de Compras", utilizador=nome)

    animar_carregamento("A carregar histórico...")
    resp = (
        supabase.table("compras")
        .select("produto_id, data")
        .eq("user_id", user_id)
        .order("data", desc=True)
        .execute()
    )

    compras = resp.data or []
    if not compras:
        notificar("📭 Ainda não fizeste nenhuma compra.", "info")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    tabela = []
    total_gasto = 0
    for c in compras:
        prod = supabase.table("produtos").select("nome, preco, plataforma").eq("id", c["produto_id"]).execute()
        if not prod.data:
            continue
        p = prod.data[0]
        total_gasto += p["preco"]
        data = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
        tabela.append([p["nome"], p["plataforma"], f"€{p['preco']:.2f}", data])

    print(Fore.CYAN + "\n🧾 Histórico de Compras" + Style.RESET_ALL)
    print(tabulate(tabela, headers=["Produto", "Plataforma", "Preço", "Data"], tablefmt="fancy_grid"))
    print(f"\n💰 Total gasto: {Fore.YELLOW}€{total_gasto:.2f}{Style.RESET_ALL}")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")


def historico_detalhado(user_id, nome):
    """Mostra o histórico detalhado de compras do utilizador.

    Agrupa as compras por produto, mostrando:
    - Nome do produto
    - Plataforma
    - Quantidade total adquirida
    - Preço unitário
    - Subtotal por produto

    A informação é mostrada no terminal numa tabela formatada.

    Args:
        user_id (int | str): ID do utilizador na base de dados.
        nome (str): Nome do utilizador para exibição na UI.
    """
    limpar_terminal()
    cabecalho("Histórico Detalhado", utilizador=nome)

    animar_carregamento("A carregar detalhes de compra...")
    resp = (
        supabase.table("compras")
        .select("produto_id, data")
        .eq("user_id", user_id)
        .order("data", desc=True)
        .execute()
    )

    compras = resp.data or []
    if not compras:
        notificar("📭 Ainda não fizeste nenhuma compra.", "info")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    agrupado = {}
    for c in compras:
        pid = c["produto_id"]
        agrupado[pid] = agrupado.get(pid, 0) + 1

    tabela = []
    total_gasto = 0
    for pid, qtd in agrupado.items():
        p = supabase.table("produtos").select("nome, preco, plataforma").eq("id", pid).execute().data
        if not p:
            continue
        prod = p[0]
        subtotal = prod["preco"] * qtd
        total_gasto += subtotal
        tabela.append([prod["nome"], prod["plataforma"], qtd, f"€{prod['preco']:.2f}", f"€{subtotal:.2f}"])

    print(Fore.MAGENTA + "\n📦 Histórico Detalhado de Compras\n" + Style.RESET_ALL)
    print(tabulate(tabela, headers=["Produto", "Plataforma", "Qtd", "Preço Unit.", "Subtotal"], tablefmt="fancy_grid"))
    print(f"\n💰 Total gasto: {Fore.YELLOW}€{total_gasto:.2f}{Style.RESET_ALL}")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")


# === Interface ===
def menu_compras():
    """Menu principal de compras/carrinho na interface de linha de comando.

    Este menu permite ao utilizador:
        1. Adicionar produto ao carrinho.
        2. Ver carrinho atual.
        3. Remover item do carrinho.
        4. Finalizar compra.
        5. Ver histórico simples de compras.
        6. Ver histórico detalhado de compras.
        0. Voltar (sair do menu).

    A função depende de uma sessão válida, carregada a partir
    do ficheiro ``sessao.json``. Caso não exista sessão, o
    utilizador é informado de que precisa fazer login.

    Returns:
        None: A função é interativa e não devolve valor.
    """
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Carrinho")
        notificar("⛔ Precisas de fazer login para aceder às compras.", "erro")
        rodape()
        input("\nENTER para voltar...")
        return

    user_id = sessao["id"]
    nome = sessao["nome"]

    while True:
        limpar_terminal()
        cabecalho("Carrinho de Compras", utilizador=nome)

        print(Fore.MAGENTA + "🛒 Menu de Compras" + Style.RESET_ALL)
        print("-" * 50)
        print("1️⃣  Adicionar produto ao carrinho")
        print("2️⃣  Ver carrinho atual")
        print("3️⃣  Remover item")
        print("4️⃣  Finalizar compra")
        print("5️⃣  Ver histórico simples")
        print("6️⃣  Ver histórico detalhado")
        print("0️⃣  Voltar")
        escolha = input("\n👉 Escolha uma opção: ").strip()

        carrinho_id = obter_ou_criar_carrinho(user_id)

        if escolha == "1":
            termo = input("🔍 Digite parte do nome do produto: ").strip()
            animar_carregamento("A procurar produtos...")
            produtos = (
                supabase.table("produtos")
                .select("id, nome, preco, plataforma")
                .ilike("nome", f"%{termo}%")
                .execute()
                .data
            )

            if not produtos:
                notificar("❌ Nenhum produto encontrado.", "erro")
                input("\nENTER para voltar...")
                continue

            print("\n📋 Produtos encontrados:")
            for i, p in enumerate(produtos, start=1):
                print(f"{i}. {p['nome']} ({p['plataforma']}) - €{p['preco']:.2f}")

            try:
                idx = int(input("\nEscolha o número do produto: ")) - 1
                produto = produtos[idx]
                qtd = int(input("Quantidade: "))
                adicionar_item(carrinho_id, produto["id"], qtd, produto["preco"])
                notificar(f"✅ {produto['nome']} adicionado ao carrinho.", "sucesso")
            except Exception:
                notificar("❌ Erro ao adicionar produto.", "erro")
            input("\nENTER para continuar...")

        elif escolha == "2":
            itens = listar_itens(carrinho_id)
            limpar_terminal()
            cabecalho("Carrinho Atual", utilizador=nome)

            if not itens:
                notificar("🛒 O teu carrinho está vazio.", "info")
            else:
                tabela = [
                    [i["nome"], i["quantidade"], f"€{i['preco_unitario']:.2f}", f"€{i['total']:.2f}"]
                    for i in itens
                ]
                print(tabulate(tabela, headers=["Produto", "Qtd", "Preço Unit.", "Total"], tablefmt="fancy_grid"))
                print(f"\n💰 Total: {Fore.YELLOW}€{calcular_total(carrinho_id):.2f}{Style.RESET_ALL}")

            rodape(utilizador=nome)
            input("\nENTER para voltar...")

        elif escolha == "3":
            itens = listar_itens(carrinho_id)
            if not itens:
                notificar("🛒 Carrinho vazio.", "info")
                input("\nENTER para voltar...")
                continue

            print("\nItens no carrinho:")
            for i, item in enumerate(itens, start=1):
                print(f"{i}. {item['nome']} ({item['quantidade']}x)")

            termo = input("\nDigite parte do nome do produto a remover: ").strip()
            animar_carregamento("A remover item...")
            produto_resp = supabase.table("produtos").select("id").ilike("nome", f"%{termo}%").execute()
            if not produto_resp.data:
                notificar("❌ Produto não encontrado.", "erro")
                input("\nENTER para voltar...")
                continue

            remover_item(carrinho_id, produto_resp.data[0]["id"])
            notificar("🗑️ Produto removido do carrinho.", "alerta")
            input("\nENTER para voltar...")

        elif escolha == "4":
            finalizar_carrinho(carrinho_id, user_id)
            input("\nENTER para voltar...")

        elif escolha == "5":
            historico_compras(user_id, nome)

        elif escolha == "6":
            historico_detalhado(user_id, nome)

        elif escolha == "0":
            break

        else:
            notificar("❌ Opção inválida.", "erro")
            input("\nENTER para continuar...")


# === Execução direta ===
if __name__ == "__main__":
    menu_compras()
