"""
Módulo de comentários de produtos (terminal).

Funcionalidades principais:
- Cliente: criar e remover os próprios comentários.
- Admin: aprovar/rejeitar e remover comentários.
- Listar comentários aprovados por produto.

Tabelas envolvidas (Supabase/Postgres):
- `produtos` (id, nome, ...)
- `comentarios` (id, user_id, produto_id, texto, aprovado)
"""

from db import supabase
from datetime import datetime
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from tabulate import tabulate
from pathlib import Path
import json
import sys

SESSAO_PATH = Path(__file__).parent / "sessao.json"


# === Sessão ===
def carregar_sessao():
    """
    Carrega a sessão do utilizador a partir do ficheiro `sessao.json`.

    Returns:
        dict | None: Dicionário com chaves como `id`, `nome`, `tipo`, ou `None` se não existir/invalidar.
    """
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# === Notificação colorida ===
def notificar(msg, tipo="info"):
    """
    Apresenta mensagem colorida no terminal com ícone associado.

    Args:
        msg (str): Texto da mensagem.
        tipo (str): 'info' | 'sucesso' | 'erro' | 'alerta'.

    Side Effects:
        - Imprime no terminal com estilos do `colorama`.
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


# === Funções de comentários ===
def fazer_comentario(user_id, nome):
    """
    Cria um novo comentário pendente de aprovação para um produto.

    Fluxo:
        1) Pede o nome (ou parte) do produto.
        2) Pesquisa em `produtos` com `ilike`.
        3) Resolve ambiguidade (se houver mais de um).
        4) Insere comentário em `comentarios` com `aprovado = False`.

    Args:
        user_id (str): ID do utilizador autor do comentário.
        nome (str): Nome do utilizador (UI).

    Side Effects:
        - I/O no terminal (inputs/prints).
        - Escrita na tabela `comentarios`.
    """
    limpar_terminal()
    cabecalho("Fazer Comentário", utilizador=nome)

    produto = input("\n🕹️ Nome do produto: ").strip()
    animar_carregamento("A procurar produto...")
    produtos = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute().data

    if not produtos:
        notificar("❌ Produto não encontrado.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    if len(produtos) > 1:
        print("\n📋 Produtos encontrados:")
        for i, p in enumerate(produtos, start=1):
            print(f"{i}. {p['nome']}")
        try:
            idx = int(input("\nNúmero do produto: ")) - 1
            produto_id = produtos[idx]["id"]
        except:
            notificar("⚠️ Escolha inválida.", "erro")
            return
    else:
        produto_id = produtos[0]["id"]

    texto = input("\n💬 Escreva o seu comentário: ").strip()

    animar_carregamento("A guardar comentário...")
    supabase.table("comentarios").insert({
        "user_id": user_id,
        "texto": texto,
        "produto_id": produto_id,
        "aprovado": False
    }).execute()

    notificar("✅ Comentário enviado para aprovação!", "sucesso")
    rodape(utilizador=nome)
    input("\nENTER para voltar...")


def julgar_comentario(nome):
    """
    Lista comentários pendentes e permite aprovar/rejeitar.

    Args:
        nome (str): Nome do utilizador (UI).

    Side Effects:
        - Lê `comentarios` (aprovado = False).
        - Atualiza (aprova) ou apaga (rejeita) o registo selecionado.
        - I/O no terminal.
    """
    limpar_terminal()
    cabecalho("Aprovar Comentários", utilizador=nome)
    animar_carregamento("A carregar comentários pendentes...")

    comentarios = supabase.table("comentarios").select("*").eq("aprovado", False).execute().data
    if not comentarios:
        notificar("📭 Não há comentários pendentes.", "info")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    tabela = [[i+1, c["id"], c["texto"]] for i, c in enumerate(comentarios)]
    print(tabulate(tabela, headers=["Nº", "ID", "Comentário"], tablefmt="fancy_grid"))

    try:
        idx = int(input("\nNúmero do comentário a julgar: ")) - 1
        comentario_id = comentarios[idx]["id"]
    except:
        notificar("❌ Escolha inválida.", "erro")
        return

    decisao = input("Aprovar este comentário? (s/n): ").lower()
    if decisao == "s":
        supabase.table("comentarios").update({"aprovado": True}).eq("id", comentario_id).execute()
        notificar("✅ Comentário aprovado!", "sucesso")
    elif decisao == "n":
        supabase.table("comentarios").delete().eq("id", comentario_id).execute()
        notificar("🗑️ Comentário rejeitado e removido.", "alerta")
    else:
        notificar("⚠️ Opção inválida.", "erro")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")


def listar_comentario_por_produto(nome):
    """
    Mostra comentários aprovados de um produto escolhido.

    Args:
        nome (str): Nome do utilizador (UI).

    Side Effects:
        - Pesquisa o produto por nome (ilike).
        - Lista comentários aprovados em `comentarios`.
        - I/O no terminal.
    """
    limpar_terminal()
    cabecalho("Listar Comentários", utilizador=nome)

    produto = input("🕹️ Produto para ver comentários: ").strip()
    animar_carregamento("A carregar comentários...")

    produtos = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute().data
    if not produtos:
        notificar("❌ Produto não encontrado.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    produto_id = produtos[0]["id"]
    comentarios = (
        supabase.table("comentarios")
        .select("*")
        .eq("produto_id", produto_id)
        .eq("aprovado", True)
        .execute()
        .data
    )

    if not comentarios:
        notificar("📭 Nenhum comentário aprovado para este produto.", "info")
    else:
        tabela = [[i+1, c["texto"]] for i, c in enumerate(comentarios)]
        print(tabulate(tabela, headers=["Nº", "Comentário"], tablefmt="fancy_grid"))

    rodape(utilizador=nome)
    input("\nENTER para voltar...")


def remover_comentario_cliente(user_id, nome):
    """
    Permite ao cliente remover um comentário próprio num produto.

    Args:
        user_id (str): ID do utilizador (autor).
        nome (str): Nome do utilizador (UI).

    Side Effects:
        - Lê comentários do `user_id` para um produto escolhido.
        - Apaga o comentário selecionado caso o utilizador confirme.
        - I/O no terminal.
    """
    limpar_terminal()
    cabecalho("Remover Comentário", utilizador=nome)

    produto = input("🕹️ Produto do comentário: ").strip()
    animar_carregamento("A procurar comentários...")

    produtos = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute().data
    if not produtos:
        notificar("❌ Produto não encontrado.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    produto_id = produtos[0]["id"]
    comentarios = (
        supabase.table("comentarios")
        .select("*")
        .eq("produto_id", produto_id)
        .eq("user_id", user_id)
        .execute()
        .data
    )

    if not comentarios:
        notificar("📭 Não há comentários teus neste produto.", "info")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    tabela = [[i+1, c["texto"]] for i, c in enumerate(comentarios)]
    print(tabulate(tabela, headers=["Nº", "Comentário"], tablefmt="fancy_grid"))

    try:
        idx = int(input("\nNúmero do comentário a remover: ")) - 1
        comentario_id = comentarios[idx]["id"]
    except:
        notificar("❌ Escolha inválida.", "erro")
        return

    if input("Confirmar remoção? (s/n): ").lower() == "s":
        supabase.table("comentarios").delete().eq("id", comentario_id).execute()
        notificar("🗑️ Comentário removido com sucesso.", "alerta")
    else:
        notificar("❌ Remoção cancelada.", "erro")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")


def remover_comentario_admin(nome):
    """
    Permite ao administrador remover qualquer comentário de um produto.

    Args:
        nome (str): Nome do utilizador (admin) para UI.

    Side Effects:
        - Pesquisa produto, lista todos os comentários (aprovados ou não).
        - Apaga o comentário selecionado mediante confirmação.
        - I/O no terminal.
    """
    limpar_terminal()
    cabecalho("Remover Comentário (Admin)", utilizador=nome)

    produto = input("🕹️ Produto a revisar: ").strip()
    animar_carregamento("A carregar comentários...")

    produtos = supabase.table("produtos").select("id", "nome").ilike("nome", f"%{produto}%").execute().data
    if not produtos:
        notificar("❌ Produto não encontrado.", "erro")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    produto_id = produtos[0]["id"]
    comentarios = supabase.table("comentarios").select("*").eq("produto_id", produto_id).execute().data

    if not comentarios:
        notificar("📭 Nenhum comentário encontrado.", "info")
    else:
        tabela = [[i+1, c["id"], c["texto"], "✅" if c["aprovado"] else "⏳"] for i, c in enumerate(comentarios)]
        print(tabulate(tabela, headers=["Nº", "ID", "Comentário", "Estado"], tablefmt="fancy_grid"))

        try:
            idx = int(input("\nNúmero do comentário a remover: ")) - 1
            comentario_id = comentarios[idx]["id"]
        except:
            notificar("❌ Escolha inválida.", "erro")
            return

        if input("Confirmar remoção? (s/n): ").lower() == "s":
            supabase.table("comentarios").delete().eq("id", comentario_id).execute()
            notificar("🗑️ Comentário removido com sucesso.", "alerta")
        else:
            notificar("Remoção cancelada.", "info")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")


# === Menu principal ===
def menu_comentarios():
    """
    Loop principal de comentários.

    Fluxo para cliente:
        1) Fazer comentário
        2) Remover comentário

    Fluxo para admin:
        1) Listar por produto
        2) Aprovar/Rejeitar
        3) Remover comentário

    Side Effects:
        - Exibe menus, lê sessão e executa ações de acordo com o tipo.
        - I/O no terminal.
    """
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Comentários")
        notificar("⛔ Precisas de fazer login para aceder aos comentários.", "erro")
        rodape()
        input("\nENTER para voltar...")
        return

    user_id = sessao["id"]
    nome = sessao["nome"]
    tipo = sessao["tipo"]

    while True:
        limpar_terminal()
        cabecalho("Comentários", utilizador=nome)

        if tipo == "cliente":
            print(Fore.MAGENTA + "💬 Menu de Comentários" + Style.RESET_ALL)
            print("-" * 50)
            print("1️⃣ Fazer comentário")
            print("2️⃣ Remover comentário")
            print("0️⃣ Voltar")

            escolha = input("\n👉 Escolha uma opção: ").strip()
            if escolha == "1":
                fazer_comentario(user_id, nome)
            elif escolha == "2":
                remover_comentario_cliente(user_id, nome)
            elif escolha == "0":
                break
            else:
                notificar("❌ Opção inválida.", "erro")
                input("\nENTER para continuar...")

        elif tipo == "admin":
            print(Fore.CYAN + "🛠️ Painel de Administração de Comentários" + Style.RESET_ALL)
            print("-" * 50)
            print("1️⃣ Listar comentários por produto")
            print("2️⃣ Aprovar/Rejeitar comentários")
            print("3️⃣ Remover comentário")
            print("0️⃣ Voltar")

            escolha = input("\n👉 Escolha uma opção: ").strip()
            if escolha == "1":
                listar_comentario_por_produto(nome)
            elif escolha == "2":
                julgar_comentario(nome)
            elif escolha == "3":
                remover_comentario_admin(nome)
            elif escolha == "0":
                break
            else:
                notificar("❌ Opção inválida.", "erro")
                input("\nENTER para continuar...")


# === Execução direta ===
if __name__ == "__main__":
    menu_comentarios()