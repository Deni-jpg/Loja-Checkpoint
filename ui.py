import shutil
import sys, time
from datetime import datetime
from colorama import Fore, Style

def limpar_terminal():
    import os
    os.system("cls" if os.name == "nt" else "clear")

def cabecalho(secao_nome, utilizador=None, tema="dark"):
    """Exibe o cabeçalho padrão da Loja Checkpoint"""
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
    """Mostra uma animação curta de carregamento."""
    simbolos = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for _ in range(2):  # Dura cerca de 2 segundos
        for s in simbolos:
            sys.stdout.write(f"\r{Fore.CYAN}{s} {mensagem}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r✅ Concluído!\n")
    time.sleep(0.5)

def rodape(utilizador=None, tema="dark"):
    """Mostra o rodapé padrão"""
    largura = shutil.get_terminal_size().columns
    texto_tema = f"🎨 Tema: {tema.capitalize()}"
    texto_user = f"👤 Utilizador: {utilizador}" if utilizador else "👤 Utilizador: não autenticado"
    assinatura = "🏁 Loja Checkpoint 2025"
    linha = Fore.LIGHTBLACK_EX + "═" * largura + Style.RESET_ALL
    rodape = f"{texto_tema} | {texto_user} | {assinatura}"
    print("\n" + linha)
    print(Fore.LIGHTWHITE_EX + rodape.center(largura) + Style.RESET_ALL)
    print(linha)
