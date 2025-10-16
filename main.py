import sys
import subprocess
import json
import time
from pathlib import Path
from itertools import cycle

cliente_logado = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False

# Diretório base e config
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
last_choice = None

# Módulos disponíveis
MODULE_MAP = {
    "1": ("👤 Cliente (Login / Registo)", "clientes.py"),
    "2": ("📦 Produtos", "produtos.py"),
    "3": ("🛒 Compras", "compras.py"),
    "4": ("💬 Comentários", "comentarios.py"),
    "5": ("⚙️ Configurações", None),
    "0": ("🚪 Sair", None)
}

# Cores por tema
THEME_COLORS = {
    "dark": {
        "header": Fore.BLUE,
        "title": Fore.GREEN,
        "option": Fore.CYAN,
        "exit": Fore.RED,
        "prompt": Fore.YELLOW,
        "info": Fore.MAGENTA
    },
    "light": {
        "header": Fore.BLACK,
        "title": Fore.BLUE,
        "option": Fore.MAGENTA,
        "exit": Fore.RED,
        "prompt": Fore.GREEN,
        "info": Fore.CYAN
    }
}

TEXTS = {
    "welcome": "👋 Bem-vindo à Loja Checkpoint!",
    "choose": "👉 Escolha uma opção: ",
    "invalid": "❌ Opção inválida. Tente novamente.",
    "exit": "👋 A sair do sistema. Obrigado por visitar!",
    "back": "🔙 Pressione ENTER para voltar ao menu...",
    "running": "▶ A executar",
    "not_found": "⚠️  Ficheiro não encontrado",
    "done": "✅ Execução concluída.",
    "interrupted": "⛔ Execução interrompida.",
    "error": "❌ Erro ao executar o ficheiro:",
    "config_title": "⚙️ Alterar configurações",
    "theme_prompt": "🎨 Tema (dark/light): ",
    "config_saved": "✅ Tema atualizado.",
    "config_invalid": "❌ Valor inválido. Nenhuma alteração feita."
}

# Carrega ou cria config.json
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
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(color(f"Erro ao guardar configurações: {e}", Fore.RED))

# Aplica cor se possível
def color(text, color_code):
    if not COLOR_ENABLED:
        return text
    return f"{color_code}{text}{Style.RESET_ALL}"

# Executa script
def run_script(filename: str):
    global cliente_logado
    path = BASE_DIR / filename
    if not path.exists():
        print(color(f"{TEXTS['not_found']}: {filename}", Fore.RED))
        return

    print(color(f"\n{TEXTS['running']} {filename}...\n", Fore.CYAN))
    try:
        subprocess.run([sys.executable, str(path)], check=False)
        print(color(f"\n{TEXTS['done']}", Fore.GREEN))

        # se o script executado for o de login, marca como logado
        if filename == "clientes.py":
            cliente_logado = True

    except KeyboardInterrupt:
        print(color(f"\n{TEXTS['interrupted']}", Fore.YELLOW))
    except Exception as e:
        print(color(f"\n{TEXTS['error']} {e}", Fore.RED))

# Cabeçalho animado
def show_menu_header(theme, frame):
    colors = THEME_COLORS[theme]
    title = f"🛍️  LOJA CHECKPOINT - MENU GLOBAL {frame}"
    print(color("\n" + "═" * 50, colors["header"]))
    print(color(title.center(50), colors["title"]))
    print(color("═" * 50, colors["header"]))
    time.sleep(0.2)

# Opções do menu com animação
def show_menu_options(theme):
    colors = THEME_COLORS[theme]
    for key, (label, _) in MODULE_MAP.items():
        # esconde a opção de login se o cliente já estiver logado
        if cliente_logado and key == "1":
            continue
        emoji_color = colors["exit"] if key == "0" else colors["option"]
        star = " ⭐" if key == last_choice else ""
        print(color(f"{key}️⃣  {label}{star}", emoji_color))
        time.sleep(0.1)
    print(color("─" * 50, colors["header"]))
    time.sleep(0.1)

# Menu principal
def main_menu():
    global last_choice
    config = load_config()
    theme = config["theme"]
    frame_cycle = cycle(["◐", "◓", "◑", "◒"])

    print(color(f"\n{TEXTS['welcome']}", THEME_COLORS[theme]["info"]))
    while True:
        frame = next(frame_cycle)
        show_menu_header(theme, frame)
        show_menu_options(theme)

        escolha = input(color(TEXTS["choose"], THEME_COLORS[theme]["prompt"])).strip()

        if escolha not in MODULE_MAP:
            print(color(f"{TEXTS['invalid']}\n", Fore.RED))
            time.sleep(0.5)
            continue

        label, filename = MODULE_MAP[escolha]
        last_choice = escolha

        if escolha == "0":
            print(color(f"\n{TEXTS['exit']}", THEME_COLORS[theme]["title"]))
            break

        if escolha == "5":
            print(color(f"\n{TEXTS['config_title']}", THEME_COLORS[theme]["info"]))
            new_theme = input(TEXTS["theme_prompt"]).strip().lower()

            if new_theme in THEME_COLORS:
                config["theme"] = new_theme
                save_config(config)
                theme = new_theme  # Aplica dinamicamente
                print(color(TEXTS["config_saved"], Fore.GREEN))
            else:
                print(color(TEXTS["config_invalid"], Fore.RED))
            input(color(f"\n{TEXTS['back']}", THEME_COLORS[theme]["prompt"]))
            continue

        run_script(filename)
        
        if escolha != "4":
            input(color(f"\n{TEXTS['back']}", THEME_COLORS[theme]["prompt"]))

if __name__ == "__main__":
    main_menu()
