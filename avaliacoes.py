"""
Módulo de avaliações de produtos (terminal).

Funcionalidades:
- Cliente avalia um produto comprado (1 a 5 estrelas + comentário opcional).
- Visualização de médias por produto com representação em estrelas.
- Menu de avaliações (cliente e admin) integrando com UI em terminal.

Dependências:
- Supabase (tabelas: `produtos`, `compras`, `avaliacoes`)
- Utilitários de UI (cabecalho, rodape, limpar_terminal, animar_carregamento)
- `colorama` e `tabulate` para visualização amigável.
"""

from db import supabase
from datetime import datetime
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from pathlib import Path
from tabulate import tabulate
import json
import sys

SESSAO_PATH = Path(__file__).parent / "sessao.json"


# === FUNÇÕES DE SESSÃO ===
def carregar_sessao():
    """
    Carrega a sessão do utilizador a partir do ficheiro local `sessao.json`.

    Returns:
        dict | None: Dicionário com chaves esperadas (`id`, `nome`, `tipo`) ou `None`.
    """
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# === NOTIFICAÇÕES COLORIDAS ===
def notificar(mensagem, tipo="info"):
    """
    Apresenta uma notificação colorida no terminal.

    Args:
        mensagem (str): Texto a mostrar.
        tipo (str): 'info', 'sucesso', 'erro' ou 'alerta'.

    Side Effects:
        - Imprime no terminal usando `colorama`.
    """
    cores = {
        "info": Fore.CYAN,
        "sucesso": Fore.GREEN,
        "erro": Fore.RED,
        "alerta": Fore.YELLOW
    }
    cor = cores.get(tipo, Fore.WHITE)
    print(f"{cor}🔔 {mensagem}{Style.RESET_ALL}")


# === FUNÇÃO DE RENDERIZAÇÃO DE ESTRELAS ===
def render_stars(media):
    """
    Converte um valor float (1.0–5.0) numa barra de estrelas legível.

    Exemplo:
        4.5 -> "⭐⭐⭐⭐✩" (✩ como meia estrela)

    Args:
        media (float): Média calculada do produto (0–5).

    Returns:
        str: String com estrelas cheias e vazias.
    """
    cheias = int(media)
    meia = (media - cheias) >= 0.5
    estrelas = "⭐" * cheias
    if meia and cheias < 5:
        estrelas += "✩"
    estrelas += "☆" * (5 - len(estrelas))
    return estrelas


# === AVALIAR PRODUTO ===
def avaliar_produto(user_id, nome):
    """
    Permite ao utilizador avaliar um produto que já tenha comprado.

    Fluxo:
        - Busca produtos por termo (ilike no nome).
        - Valida se o utilizador comprou o produto selecionado.
        - Upsert em `avaliacoes` com estrelas (1–5) e comentário opcional.

    Args:
        user_id (str): ID do utilizador autenticado.
        nome (str): Nome do utilizador (UI).

    Returns:
        None

    Side Effects:
        - Lê tabelas `produtos` e `compras`.
        - Grava/atualiza registo em `avaliacoes`.
        - Interação completa via terminal.
    """
    limpar_terminal()
    cabecalho("Avaliar Produto", utilizador=nome)

    termo = input("🔎 Digite parte do nome do produto: ").strip()
    animar_carregamento("A procurar produtos...")
    produtos = (
        supabase.table("produtos")
        .select("id, nome")
        .ilike("nome", f"%{termo}%")
        .execute()
        .data
    )

    if not produtos:
        notificar("❌ Produto não encontrado.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    print("\n🎮 Produtos encontrados:")
    for i, p in enumerate(produtos, start=1):
        print(f"{i}. {p['nome']}")

    try:
        index = int(input("\n👉 Escolha o número do produto: ")) - 1
        produto_id = produtos[index]["id"]
    except:
        notificar("❌ Escolha inválida.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    animar_carregamento("A verificar compras...")
    compras = (
        supabase.table("compras")
        .select("id")
        .eq("user_id", user_id)
        .eq("produto_id", produto_id)
        .execute()
    )
    if not compras.data:
        notificar("⚠️ Só podes avaliar produtos que já compraste.", "alerta")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    ja_avaliou = (
        supabase.table("avaliacoes")
        .select("*")
        .eq("user_id", user_id)
        .eq("produto_id", produto_id)
        .execute()
    )
    if ja_avaliou.data:
        notificar("⚠️ Já existe uma avaliação. A tua avaliação será atualizada.", "alerta")

    try:
        estrelas = int(input("⭐ Classificação (1 a 5 estrelas): "))
        if estrelas < 1 or estrelas > 5:
            raise ValueError
    except ValueError:
        notificar("❌ Valor inválido. Insere um número entre 1 e 5.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    comentario = input("💬 Comentário (opcional): ").strip()

    supabase.table("avaliacoes").upsert({
        "user_id": user_id,
        "produto_id": produto_id,
        "estrelas": estrelas,
        "comentario": comentario,
        "data": datetime.now().isoformat()
    }).execute()

    notificar(f"✅ Avaliação registada: {estrelas} ⭐ para {produtos[index]['nome']}", "sucesso")
    rodape(utilizador=nome)
    input("\nENTER para voltar...")


# === VER MÉDIA DE AVALIAÇÕES ===
def ver_media_avaliacoes(nome):
    """
    Apresenta uma tabela com médias de avaliação por produto.

    Args:
        nome (str): Nome do utilizador para UI (cliente/admin).

    Returns:
        None

    Side Effects:
        - Lê `produtos` e `avaliacoes`.
        - Calcula média e total de avaliações por produto.
        - Imprime tabela com estrelas e estatísticas.
    """
    limpar_terminal()
    cabecalho("Médias de Avaliação", utilizador=nome)
    animar_carregamento("A calcular médias...")

    produtos = supabase.table("produtos").select("id, nome").execute().data
    if not produtos:
        notificar("❌ Nenhum produto encontrado.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    tabela = []
    for p in produtos:
        avals = (
            supabase.table("avaliacoes")
            .select("estrelas")
            .eq("produto_id", p["id"])
            .execute()
            .data
        )
        if avals:
            media = sum(a["estrelas"] for a in avals) / len(avals)
            tabela.append([
                p["nome"],
                render_stars(media),
                f"{media:.1f}/5",
                f"{len(avals)} avaliações"
            ])
        else:
            tabela.append([p["nome"], "—", "—", "Sem avaliações"])

    print("\n" + Fore.MAGENTA + "📊 Avaliações de Produtos\n" + Style.RESET_ALL)
    print(tabulate(tabela, headers=["Produto", "Classificação", "Média", "Total"], tablefmt="fancy_grid"))
    rodape(utilizador=nome)
    input("\nENTER para voltar...")


# === MENU PRINCIPAL ===
def menu_avaliacoes():
    """
    Loop de menu para funcionalidades de avaliação.

    Comportamento:
        - Se não houver sessão válida, informa e retorna ao chamador.
        - Para clientes: permite avaliar produto e ver médias.
        - Para admin: mostra diretamente as médias.

    Returns:
        None
    """
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Avaliações")
        notificar("⛔ Precisas de fazer login para aceder às avaliações.", "erro")
        rodape()
        input("\nENTER para voltar...")
        return

    user_id = sessao["id"]
    nome = sessao.get("nome", "Utilizador")
    tipo = sessao.get("tipo", "cliente")

    while True:
        limpar_terminal()
        cabecalho("Avaliações", utilizador=nome)

        if tipo == "cliente":
            print(Fore.MAGENTA + "⭐ Menu de Avaliações" + Style.RESET_ALL)
            print("-" * 50)
            print("1️⃣ Avaliar um produto comprado")
            print("2️⃣ Ver médias de avaliação")
            print("0️⃣ Voltar")

            escolha = input("\n👉 Escolha uma opção: ").strip()
            if escolha == "1":
                avaliar_produto(user_id, nome)
            elif escolha == "2":
                ver_media_avaliacoes(nome)
            elif escolha == "0":
                break
            else:
                notificar("❌ Opção inválida.", "erro")
                input("\nENTER para continuar...")

        elif tipo == "admin":
            # Para admin, mostra as médias diretamente e sai
            ver_media_avaliacoes(nome)
            break


# === EXECUÇÃO DIRETA ===
if __name__ == "__main__":
    menu_avaliacoes()