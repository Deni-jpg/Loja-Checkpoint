"""
Gestão de produtos (terminal) para a Loja Checkpoint.

Este módulo oferece operações de administração e consulta de produtos
integradas ao terminal, usando Supabase como fonte de dados.

Funcionalidades principais:
- Admin:
  - Adicionar, atualizar e remover produtos.
  - Listar produtos com stock baixo.
  - Listar Top 3 produtos mais vendidos.
- Cliente:
  - Visualizar catálogo (delegado a `produtos_utils.listar_produtos`).
- Sessão:
  - Requer sessão válida em `sessao.json` com chaves mínimas: `id`, `nome`, `tipo`.

Tabelas utilizadas (ver `db.sql`):
- public.produtos (id, nome, plataforma, preco, stock, vendas, descricao)

Dependências:
- Supabase (cliente em `db.supabase`)
- Utilitários de UI (`ui.cabecalho`, `ui.rodape`, `ui.limpar_terminal`, `ui.animar_carregamento`)
- `colorama` e `tabulate` para experiência visual no terminal
"""

from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from tabulate import tabulate
from produtos_utils import listar_produtos  # usa o utilitário visual/dados
from pathlib import Path
import json, sys

SESSAO_PATH = Path(__file__).parent / "sessao.json"


# === Sessão ===
def carregar_sessao():
    """
    Carrega a sessão do utilizador a partir de `sessao.json`.

    Returns:
        dict | None: Dicionário com `id`, `nome`, `tipo` se existir; `None` caso contrário.
    """
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# === Notificação colorida ===
def notificar(msg, tipo="info"):
    """
    Mostra uma notificação colorida no terminal.

    Args:
        msg (str): Mensagem a apresentar.
        tipo (str): Um de {'info', 'sucesso', 'erro', 'alerta'}.

    Side Effects:
        - Imprime no terminal com estilos `colorama`.
    """
    cores = {
        "info": Fore.CYAN,
        "sucesso": Fore.GREEN,
        "erro": Fore.RED,
        "alerta": Fore.YELLOW
    }
    icones = {
        "info": "ℹ️",
        "sucesso": "✅",
        "erro": "❌",
        "alerta": "⚠️"
    }
    print(f"{cores.get(tipo, Fore.WHITE)}{icones.get(tipo, '💬')} {msg}{Style.RESET_ALL}")


# === Validações & Leitura Segura ===
def _parse_float_pt(valor_str):
    """
    Converte string com separador decimal vírgula ou ponto em `float`.

    Args:
        valor_str (str): Ex.: "19,99", "19.99", "  9,5 ".

    Returns:
        float: Valor convertido.

    Raises:
        ValueError: Se não for possível converter para número.
    """
    return float(valor_str.replace(",", ".").strip())


def ler_texto_obrigatorio(prompt):
    """
    Lê um texto não vazio do terminal (repete até ser válido).

    Args:
        prompt (str): Prompt para input.

    Returns:
        str: Texto preenchido.
    """
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        notificar("❌ Este campo é obrigatório.", "erro")


def ler_preco_positivo(prompt):
    """
    Lê um preço > 0 (aceita vírgula), com validação.

    Args:
        prompt (str): Prompt para input.

    Returns:
        float: Valor numérico > 0.
    """
    while True:
        bruto = input(prompt).strip()
        try:
            preco = _parse_float_pt(bruto)
            if preco <= 0:
                raise ValueError
            return preco
        except Exception:
            notificar("❌ Preço inválido. Introduz um número maior que 0 (ex.: 19,99).", "erro")


def ler_stock_nao_negativo(prompt):
    """
    Lê um stock inteiro >= 0 (com validação).

    Args:
        prompt (str): Prompt para input.

    Returns:
        int: Valor inteiro >= 0.
    """
    while True:
        bruto = input(prompt).strip()
        try:
            stock = int(bruto)
            if stock < 0:
                raise ValueError
            return stock
        except Exception:
            notificar("❌ Stock inválido. Introduz um número inteiro igual ou maior que 0.", "erro")


def ler_id_inteiro(prompt):
    """
    Lê um ID inteiro válido (com validação).

    Args:
        prompt (str): Prompt para input.

    Returns:
        int: ID inteiro.
    """
    while True:
        bruto = input(prompt).strip()
        try:
            return int(bruto)
        except Exception:
            notificar("❌ ID inválido. Introduz um número inteiro.", "erro")


def confirmar(prompt="Confirmar? (s/n): "):
    """
    Obtém confirmação simples do utilizador (apenas 's' confirma).

    Args:
        prompt (str): Prompt a apresentar.

    Returns:
        bool: `True` se o utilizador confirmou com 's'; caso contrário, `False`.
    """
    return input(prompt).strip().lower() == "s"


def validar_produto(dados):
    """
    Validação defensiva antes de escrever na BD.

    Args:
        dados (dict): Campos do produto:
            - nome (str, obrigatório)
            - plataforma (str, obrigatório)
            - preco (float, > 0)
            - stock (int, >= 0)
            - descricao (str, opcional, <= 1000 chars)

    Returns:
        tuple[bool, list[str]]: `(ok, erros)` onde `ok` indica se passou na validação,
        e `erros` contém as mensagens de erro encontradas.
    """
    erros = []
    nome = (dados.get("nome") or "").strip()
    if not nome:
        erros.append("Nome é obrigatório.")

    preco = dados.get("preco")
    if preco is None or not isinstance(preco, (int, float)) or preco <= 0:
        erros.append("Preço deve ser um número maior que 0.")

    stock = dados.get("stock")
    if stock is None or not isinstance(stock, int) or stock < 0:
        erros.append("Stock deve ser um inteiro igual ou maior que 0.")

    plataforma = (dados.get("plataforma") or "").strip()
    if not plataforma:
        erros.append("Plataforma é obrigatória.")

    descricao = (dados.get("descricao") or "").strip()
    if len(descricao) > 1000:
        erros.append("Descrição não pode exceder 1000 caracteres.")

    return (len(erros) == 0, erros)


# === Acesso auxiliar à BD ===
def obter_produto_por_id(produto_id):
    """
    Devolve um produto (dict) pelo seu ID.

    Args:
        produto_id (int): Identificador do produto.

    Returns:
        dict | None: Registo do produto ou `None` se não encontrado.

    Side Effects:
        - Em caso de erro na consulta, imprime notificação de erro.
    """
    try:
        resp = supabase.table("produtos").select("*").eq("id", produto_id).limit(1).execute()
        dados = resp.data or []
        return dados[0] if dados else None
    except Exception as ex:
        notificar(f"❌ Erro ao consultar produto: {ex}", "erro")
        return None


# === Operações (Admin) ===
def adicionar_produto(nome_utilizador):
    """
    Fluxo interativo para adicionar um novo produto.

    Args:
        nome_utilizador (str): Nome do utilizador (para UI no cabeçalho/rodapé).

    Side Effects:
        - Lê inputs do terminal.
        - Valida dados localmente.
        - Insere na tabela `produtos` via Supabase.
        - Imprime mensagens de sucesso/erro.
    """
    limpar_terminal()
    cabecalho("Adicionar Produto", utilizador=nome_utilizador)

    nome = ler_texto_obrigatorio("🕹️ Nome: ")
    plataforma = ler_texto_obrigatorio("🎮 Plataforma: ")
    preco = ler_preco_positivo("💰 Preço (€): ")
    stock = ler_stock_nao_negativo("📦 Stock: ")
    descricao = input("📝 Descrição: ").strip()

    novo_produto = {
        "nome": nome,
        "plataforma": plataforma,
        "preco": preco,
        "stock": stock,
        "descricao": descricao
    }

    ok, erros = validar_produto(novo_produto)
    if not ok:
        notificar("❌ Não foi possível adicionar o produto devido a:", "erro")
        for e in erros:
            notificar(f"- {e}", "erro")
        rodape(utilizador=nome_utilizador)
        input("\nENTER para voltar...")
        return

    try:
        animar_carregamento("A adicionar produto...")
        supabase.table("produtos").insert(novo_produto).execute()
        notificar("✅ Produto adicionado com sucesso!", "sucesso")
    except Exception as ex:
        notificar(f"❌ Erro ao adicionar produto: {ex}", "erro")

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")


def atualizar_produto(nome_utilizador):
    """
    Fluxo interativo para atualizar um produto existente.

    Args:
        nome_utilizador (str): Nome do utilizador para UI.

    Side Effects:
        - Lista produtos (modo visual) para auxiliar seleção.
        - Lê campos atualizados do terminal e executa `UPDATE` em `produtos`.
    """
    limpar_terminal()
    cabecalho("Atualizar Produto", utilizador=nome_utilizador)
    listar_produtos(modo="visual")

    produto_id = ler_id_inteiro("\n🔖 ID do produto a atualizar: ")

    # Verifica existência
    produto_atual = obter_produto_por_id(produto_id)
    if not produto_atual:
        notificar("❌ Produto inexistente. Verifica o ID e tenta novamente.", "erro")
        rodape(utilizador=nome_utilizador)
        input("\nENTER para voltar...")
        return

    nome = ler_texto_obrigatorio("🕹️ Novo nome: ")
    plataforma = ler_texto_obrigatorio("🎮 Nova plataforma: ")
    preco = ler_preco_positivo("💰 Novo preço (€): ")
    stock = ler_stock_nao_negativo("📦 Novo stock: ")
    descricao = input("📝 Nova descrição: ").strip()

    atualizacao = {
        "nome": nome,
        "plataforma": plataforma,
        "preco": preco,
        "stock": stock,
        "descricao": descricao
    }

    ok, erros = validar_produto(atualizacao)
    if not ok:
        notificar("❌ Não foi possível atualizar o produto devido a:", "erro")
        for e in erros:
            notificar(f"- {e}", "erro")
        rodape(utilizador=nome_utilizador)
        input("\nENTER para voltar...")
        return

    try:
        animar_carregamento("A atualizar produto...")
        supabase.table("produtos").update(atualizacao).eq("id", produto_id).execute()
        notificar("✅ Produto atualizado com sucesso!", "sucesso")
    except Exception as ex:
        notificar(f"❌ Erro ao atualizar produto: {ex}", "erro")

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")


def remover_produto(nome_utilizador):
    """
    Fluxo interativo para remover um produto existente.

    Args:
        nome_utilizador (str): Nome do utilizador (UI).

    Side Effects:
        - Confirma existência do ID.
        - Solicita confirmação do utilizador.
        - Executa `DELETE` em `produtos`.
    """
    limpar_terminal()
    cabecalho("Remover Produto", utilizador=nome_utilizador)
    listar_produtos(modo="visual")

    produto_id = ler_id_inteiro("\n🔖 ID do produto a remover: ")

    # ✅ Validação: impedir remoção de ID inexistente
    produto = obter_produto_por_id(produto_id)
    if not produto:
        notificar("❌ ID inexistente. Não é possível remover um produto que não existe.", "erro")
        rodape(utilizador=nome_utilizador)
        input("\nENTER para voltar...")
        return

    print(
        Fore.YELLOW
        + f"\nVai remover: [{produto_id}] {produto.get('nome')} "
          f"(Stock: {produto.get('stock')}, Preço: {produto.get('preco')}€)"
        + Style.RESET_ALL
    )

    if not confirmar("⚠️ Confirmar remoção? (s/n): "):
        notificar("Remoção cancelada.", "info")
        rodape(utilizador=nome_utilizador)
        input("\nENTER para voltar...")
        return

    try:
        animar_carregamento("A remover produto...")
        # Confirma quantos registos foram removidos (protege contra concorrência)
        resp = supabase.table("produtos").delete().eq("id", produto_id).select("id").execute()
        removidos = len(resp.data or [])
        if removidos == 0:
            notificar("⚠️ O produto já não existia. Nenhuma remoção efetuada.", "alerta")
        else:
            notificar("🗑️ Produto removido com sucesso!", "alerta")
    except Exception as ex:
        notificar(f"❌ Erro ao remover produto: {ex}", "erro")

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")


def listar_produtos_com_stock_baixo(nome_utilizador):
    """
    Lista os produtos com stock abaixo de um limiar (default: < 3).

    Args:
        nome_utilizador (str): Nome para UI.

    Side Effects:
        - Consulta `produtos` com `stock < 3`.
        - Imprime tabela ('Produto' x 'Stock') no terminal.
    """
    limpar_terminal()
    cabecalho("Stock Baixo", utilizador=nome_utilizador)
    animar_carregamento("A verificar stock...")

    try:
        response = supabase.table("produtos").select("nome, stock").lt("stock", 3).execute()
        produtos = response.data or []
    except Exception as ex:
        notificar(f"❌ Erro ao carregar produtos: {ex}", "erro")
        produtos = []

    if not produtos:
        notificar("📦 Nenhum produto com stock baixo!", "info")
    else:
        tabela = [[p["nome"], p["stock"]] for p in produtos]
        print(tabulate(tabela, headers=["Produto", "Stock"], tablefmt="fancy_grid"))

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")


def listar_produtos_mais_vendidos(nome_utilizador):
    """
    Mostra os 3 produtos com maior valor no campo `vendas`.

    Args:
        nome_utilizador (str): Nome para UI.

    Side Effects:
        - Consulta `produtos` ordenando `vendas` desc e limitando em 3.
        - Imprime ranking no terminal.
    """
    limpar_terminal()
    cabecalho("Top 3 Produtos Mais Vendidos", utilizador=nome_utilizador)
    animar_carregamento("A carregar dados...")

    try:
        response = supabase.table("produtos").select("nome, vendas").order("vendas", desc=True).limit(3).execute()
        produtos = response.data or []
    except Exception as ex:
        notificar(f"❌ Erro ao carregar dados: {ex}", "erro")
        produtos = []

    if not produtos:
        notificar("📭 Nenhum produto registado ainda.", "info")
    else:
        tabela = [[i+1, p["nome"], p["vendas"]] for i, p in enumerate(produtos)]
        print(tabulate(tabela, headers=["#", "Produto", "Vendas"], tablefmt="fancy_grid"))

    rodape(utilizador=nome_utilizador)
    input("\nENTER para voltar...")


# === Menu principal ===
def menu_produtos():
    """
    Loop de menu de produtos (terminal).

    Requisitos:
        - Sessão válida (ficheiro `sessao.json` com `id`, `nome`, `tipo`).
    Comportamento:
        - Se `tipo == 'admin'`: exibe opções de gestão (CRUD, stock baixo, top vendidos).
        - Se `tipo != 'admin'`: exibe menu para cliente (listar catálogo e top vendidos).

    Side Effects:
        - I/O no terminal, leituras/escritas em Supabase conforme opções.
    """
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Produtos")
        notificar("⛔ Precisas de fazer login para aceder ao menu de produtos.", "erro")
        rodape()
        input("\nENTER para voltar...")
        return

    nome = sessao["nome"]
    tipo = sessao["tipo"]

    while True:
        limpar_terminal()
        cabecalho("Menu de Produtos", utilizador=nome)

        if tipo == "admin":
            print(Fore.CYAN + "⚙️ Gestão de Produtos (Admin)" + Style.RESET_ALL)
            print("-" * 50)
            print("1️⃣ Adicionar produto")
            print("2️⃣ Listar produtos")
            print("3️⃣ Atualizar produto")
            print("4️⃣ Remover produto")
            print("5️⃣ Ver produtos com stock baixo")
            print("6️⃣ Top 3 produtos mais vendidos")
            print("0️⃣ Voltar")

            escolha = input("\n👉 Escolha uma opção: ").strip()
            match escolha:
                case "1":
                    adicionar_produto(nome)
                case "2":
                    listar_produtos(modo="visual")
                case "3":
                    atualizar_produto(nome)
                case "4":
                    remover_produto(nome)
                case "5":
                    listar_produtos_com_stock_baixo(nome)
                case "6":
                    listar_produtos_mais_vendidos(nome)
                case "0":
                    break
                case _:
                    notificar("❌ Opção inválida.", "erro")
                    input("\nENTER para continuar...")

        else:  # Cliente
            print(Fore.MAGENTA + "🎮 Catálogo de Produtos" + Style.RESET_ALL)
            print("-" * 50)
            print("1️⃣ Ver produtos disponíveis")
            print("2️⃣ Ver produtos mais vendidos")
            print("0️⃣ Voltar")

            escolha = input("\n👉 Escolha uma opção: ").strip()
            if escolha == "1":
                listar_produtos(modo="visual", utilizador=nome)
            elif escolha == "2":
                listar_produtos_mais_vendidos(nome)
            elif escolha == "0":
                break
            else:
                notificar("❌ Opção inválida.", "erro")
                input("\nENTER para continuar...")


# === Execução direta ===
if __name__ == "__main__":
    menu_produtos()