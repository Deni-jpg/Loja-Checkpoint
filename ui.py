"""
Módulo de interface de terminal (UI) da Loja Checkpoint.

Este módulo centraliza elementos visuais reutilizáveis na aplicação:
    - Limpeza do terminal
    - Cabeçalho padrão com estado do utilizador e hora atual
    - Animação de carregamento
    - Rodapé padrão com tema, utilizador e assinatura

É utilizado por vários outros módulos (menus, carrinho, produtos, etc.)
para garantir uma apresentação consistente no terminal.
"""

import shutil
import sys
import time
from datetime import datetime
from colorama import Fore, Style


def limpar_terminal():
    """Limpa o terminal da consola.

    Deteta automaticamente o sistema operativo:
        - Em Windows usa o comando ``cls``.
        - Em sistemas Unix-like (Linux, macOS) usa o comando ``clear``.

    Returns:
        None: A função apenas executa o comando de sistema.
    """
    import os
    os.system("cls" if os.name == "nt" else "clear")


def cabecalho(secao_nome, utilizador=None, tema="dark"):
    """Exibe o cabeçalho padrão da Loja Checkpoint.

    O cabeçalho inclui:
        - Nome da loja e nome da secção atual.
        - Estado do utilizador: online (verde) ou offline (vermelho).
        - Data e hora atuais.
        - Separadores com linhas horizontais.

    Args:
        secao_nome (str): Nome da secção a apresentar no cabeçalho
            (por exemplo, ``"Carrinho"`` ou ``"Catálogo de Produtos"``).
        utilizador (str | None): Nome do utilizador autenticado. Se for
            ``None``, é mostrado como offline.
        tema (str, optional): Nome do tema visual (apenas informativo
            neste contexto). Por omissão é ``"dark"``.
    """
    largura = shutil.get_terminal_size().columns
    metade = largura // 2
    cor_estado = Fore.GREEN if utilizador else Fore.RED
    estado = f"{cor_estado}{'🟢 Online como ' + utilizador if utilizador else '🔴 Offline'}{Style.RESET_ALL}"
    hora = datetime.now().strftime("🕒 %d/%m/%Y %H:%M")

    print(Fore.LIGHTBLACK_EX + "=" * largura + Style.RESET_ALL)
    print(Fore.CYAN + f"🛍️  LOJA CHECKPOINT — {secao_nome.upper()}".center(largura) + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + "=" * largura + Style.RESET_ALL)
    print(estado.ljust(metade) + f"{Fore.LIGHTWHITE_EX}{hora}{Style.RESET_ALL}".rjust(metade))
    print(Fore.LIGHTBLACK_EX + "=" * largura + Style.RESET_ALL + "\n")


def animar_carregamento(mensagem="A carregar..."):
    """Mostra uma animação curta de carregamento no terminal.

    A animação é composta por uma sequência de símbolos em movimento,
    apresentada na mesma linha, acompanhada pela mensagem fornecida.

    Duração aproximada: ~2 segundos.

    Args:
        mensagem (str, optional): Texto a mostrar ao lado da animação.
            Por omissão é ``"A carregar..."``.

    Returns:
        None: A função apenas escreve no ``stdout`` e faz pequenas pausas.
    """
    simbolos = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for _ in range(2):  # Dura cerca de 2 segundos
        for s in simbolos:
            sys.stdout.write(f"\r{Fore.CYAN}{s} {mensagem}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r✅ Concluído!\n")
    time.sleep(0.5)


def rodape(utilizador=None, tema="dark"):
    """Mostra o rodapé padrão da aplicação.

    O rodapé inclui:
        - Nome do tema atual.
        - Nome (ou ausência) do utilizador autenticado.
        - Assinatura com o nome da loja e ano.

    Args:
        utilizador (str | None): Nome do utilizador autenticado.
            Se ``None``, é indicado como "não autenticado".
        tema (str, optional): Nome do tema visual (informativo).
            Por omissão é ``"dark"``.

    Returns:
        None: Apenas escreve o rodapé no terminal.
    """
    largura = shutil.get_terminal_size().columns
    texto_tema = f"🎨 Tema: {tema.capitalize()}"
    texto_user = f"👤 Utilizador: {utilizador}" if utilizador else "👤 Utilizador: não autenticado"
    assinatura = "🏁 Loja Checkpoint 2025"
    linha = Fore.LIGHTBLACK_EX + "═" * largura + Style.RESET_ALL
    rodape_txt = f"{texto_tema} | {texto_user} | {assinatura}"
    print("\n" + linha)
    print(Fore.LIGHTWHITE_EX + rodape_txt.center(largura) + Style.RESET_ALL)
    print(linha)
