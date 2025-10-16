# main.py
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent

MODULE_MAP = {
    "1": ("Cliente(Fazer Login/Registar)", "clientes.py"),
    "2": ("Produtos", "produtos.py"),
    "3": ("Compras", "compras.py"),
    "4": ("Comentários", "comentarios.py"),
    "0": ("Sair", None)
}

def run_script(filename: str):
    path = BASE_DIR / filename
    if not path.exists():
        print(f"Ficheiro não encontrado: {filename}")
        return
    print(f"Executando {filename}...\n")
    try:
        subprocess.run([sys.executable, str(path)], check=False)
    except KeyboardInterrupt:
        print("Execução interrompida pelo utilizador.")
    except Exception as e:
        print("Erro ao executar o ficheiro:", e)

def main_menu():
    while True:
        print("\n=== Loja Checkpoint - Menu Global ===")
        for key, (label, _) in MODULE_MAP.items():
            print(f"{key} -> {label}")
        escolha = input("Escolha uma opção: ").strip()
        if escolha not in MODULE_MAP:
            print("Opção inválida. Tente novamente.")
            continue
        label, filename = MODULE_MAP[escolha]
        if escolha == "0":
            print("A sair.")
            break
        run_script(filename)

if __name__ == "__main__":
    main_menu()
