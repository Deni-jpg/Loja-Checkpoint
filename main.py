import sys, os, time, json, subprocess, random, shutil, threading
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style
from tabulate import tabulate
from db import supabase
from auth import login_utilizador, registar_utilizador

# === CONFIGURAÇÕES ===
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
SESSAO_PATH = BASE_DIR / "sessao.json"

utilizador_logado = None
stop_animation = False

# === MENU ===
MENU_ITEMS = [
    ["1", "🔐 Login", "Entrar na sua conta"],
    ["2", "🆕 Registo", "Criar uma nova conta"],
    ["3", "📦 Produtos", "Ver e procurar jogos disponíveis"],
    ["4", "🛒 Compras", "Adicionar e finalizar compras"],
    ["5", "💬 Comentários", "Ler e deixar feedback nos produtos"],
    ["7", "⭐ Avaliações", "Avaliar produtos comprados"],
    ["8", "🆚 Comparar Jogos", "Comparar preços e avaliações"],
    ["9", "🎁 Wishlist", "Guardar jogos favoritos"],
    ["6", "🛠  Configurações", "Alterar tema e preferências"],
    ["0", "🚪 Sair", "Fechar o programa"]
]

# === FUNÇÕES AUXILIARES ===
def color(text, color_code):
    return f"{color_code}{text}{Style.RESET_ALL}"

def load_config():
    default = {"theme": "dark"}
    if not CONFIG_PATH.exists():
        save_config(default)
        return default
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def guardar_sessao(user_dict):
    with open(SESSAO_PATH, "w", encoding="utf-8") as f:
        json.dump(user_dict, f)

def carregar_sessao():
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def limpar_sessao():
    if SESSAO_PATH.exists():
        os.remove(SESSAO_PATH)

def run_script(filename: str):
    path = BASE_DIR / filename
    if not path.exists():
        print(f"⚠️ Ficheiro não encontrado: {filename}")
        return
    print(f"\n▶ A executar {filename}...\n")
    subprocess.run([sys.executable, str(path)], check=False)
    print("\n✅ Execução concluída.")

# === CABEÇALHO FIXO ===
def cabecalho(nome, tema="dark"):
    largura = shutil.get_terminal_size().columns
    metade = largura // 2
    cor_estado = Fore.GREEN if nome else Fore.RED
    estado = f"{cor_estado}{'🟢 Online como ' + nome if nome else '🔴 Offline - Inicia sessão para aceder a todas as opções'}{Style.RESET_ALL}"
    agora = datetime.now().strftime("🕒 %d/%m/%Y %H:%M")

    print(Fore.LIGHTBLACK_EX + "=" * largura + Style.RESET_ALL)
    print(Fore.CYAN + "🛍️  LOJA CHECKPOINT - MENU GLOBAL".center(largura) + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + "=" * largura + Style.RESET_ALL)
    print(estado.ljust(metade) + f"{Fore.LIGHTWHITE_EX}{agora}{Style.RESET_ALL}".rjust(metade))
    print(Fore.LIGHTBLACK_EX + "=" * largura + Style.RESET_ALL + "\n")

# === RODAPÉ FIXO ===
def rodape(nome=None, tema="dark"):
    largura = shutil.get_terminal_size().columns
    texto_tema = f"🎨 Tema: {tema.capitalize()}"
    texto_user = f"👤 Utilizador: {nome}" if nome else "👤 Utilizador: não autenticado"
    assinatura = "🏁 Loja Checkpoint 2025"
    linha = Fore.LIGHTBLACK_EX + "═" * largura + Style.RESET_ALL
    rodape = f"{texto_tema} | {texto_user} | {assinatura}"
    print("\n" + linha)
    print(Fore.LIGHTWHITE_EX + rodape.center(largura) + Style.RESET_ALL)
    print(linha)

# === MENU PRINCIPAL ===
def main_menu():
    global utilizador_logado
    utilizador_logado = carregar_sessao()
    config = load_config()

    while True:
        os.system("cls" if os.name == "nt" else "clear")

        nome = utilizador_logado.get("nome") if utilizador_logado else None
        cabecalho(nome, tema=config.get("theme"))

        headers = ["Nº", "Opção", "Descrição"]
        print(tabulate(MENU_ITEMS, headers=headers, tablefmt="fancy_grid"))

        rodape(
            nome=utilizador_logado.get("nome") if utilizador_logado else None,
            tema=config.get("theme")
        )

        print("\n" + Fore.YELLOW + "👉 Escolha uma opção:" + Style.RESET_ALL, end=" ")
        escolha = input().strip()

        if escolha == "0":
            limpar_sessao()
            print("\n👋 A sair do sistema. Obrigado por visitar!\n")
            break

        elif escolha == "1":
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            user = login_utilizador(email, password)
            if user:
                perfil = supabase.table("perfil").select("nome, tipo").eq("user_id", user.id).execute()
                if perfil.data:
                    nome = perfil.data[0]["nome"]
                    tipo = perfil.data[0]["tipo"]
                    utilizador_logado = {"id": user.id, "nome": nome, "tipo": tipo, "email": user.email}
                    guardar_sessao(utilizador_logado)
                    print(f"\n✅ Bem-vindo, {nome} ({tipo})\n")
                    time.sleep(1)
                else:
                    print("⚠️ Perfil não encontrado.")
            else:
                print("⛔ Login falhou. Verifica credenciais.")
            continue

        elif escolha == "2":
            nome = input("Nome: ").strip()
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            tipo = "cliente"
            registar_utilizador(email, password, nome, tipo)
            print("✅ Registo efetuado com sucesso!\n")
            time.sleep(1)
            continue

        elif escolha == "6":
            print("\n⚙️ Alterar configurações")
            new_theme = input("🎨 Tema (dark/light): ").strip().lower()
            if new_theme in ["dark", "light"]:
                config["theme"] = new_theme
                save_config(config)
                print("✅ Tema atualizado.")
            else:
                print("❌ Valor inválido.")
            input("\n🔙 Pressione ENTER para voltar ao menu...")
            continue

        elif escolha == "3":
            run_script("produtos.py")
        elif escolha == "4":
            run_script("compras.py")
        elif escolha == "5":
            run_script("comentarios.py")
        elif escolha == "7":
            run_script("avaliacoes.py")
        elif escolha == "8":
            run_script("comparar_jogos.py")
        elif escolha == "9":
            run_script("wishlist.py")
        else:
            print("⚠️ Opção inválida.")
            time.sleep(1)

        input("\n🔙 Pressione ENTER para voltar ao menu...")

# === EXECUÇÃO ===
if __name__ == "__main__":
    main_menu()
