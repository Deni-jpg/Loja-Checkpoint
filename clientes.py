"""
Gestão de clientes e administradores (terminal).

Este módulo fornece operações básicas relacionadas a perfis de utilizador:
- registo (cliente/admin) via `auth.registar_utilizador`,
- login via `auth.login_utilizador`,
- listagem/edição/remoção de perfis na tabela `perfil` (Supabase).

⚠️ Nota: Este ficheiro contém lógica interativa de menu no topo do módulo.
Ao importá-lo noutro sítio, essa parte também será executada. Para uso com Sphinx,
as docstrings serão extraídas normalmente, mas para produção recomenda-se
mover o menu para um `if __name__ == "__main__":`.
"""

from auth import registar_utilizador, login_utilizador, logout_utilizador
from db import supabase


def editar_perfil(user_id):
    """
    Atualiza o nome do perfil de um utilizador.

    Args:
        user_id (str): Identificador do utilizador (Supabase auth.user.id).

    Side Effects:
        - Atualiza o campo `nome` na tabela `perfil`.
        - Imprime mensagens no terminal.
    """
    nome = input("Novo nome: ")
    supabase.table("perfil").update({"nome": nome}).eq("user_id", user_id).execute()
    print("Perfil editado com sucesso.")


def remover_perfil(user_id):
    """
    Remove o registo de perfil associado a um utilizador.

    Args:
        user_id (str): Identificador do utilizador (Supabase auth.user.id).

    Side Effects:
        - Apaga o registo correspondente na tabela `perfil`.
        - Imprime mensagens no terminal.
    """
    supabase.table("perfil").delete().eq("user_id", user_id).execute()
    print("Perfil removido com sucesso.")


def listar_utilizadores():
    """
    Lista, no terminal, os perfis existentes com nome e tipo.

    Side Effects:
        - Lê a tabela `perfil` (campos `user_id`, `nome`, `tipo`).
        - Imprime a lista enumerada no terminal.
    """
    response = supabase.table("perfil").select('user_id', 'nome', 'tipo').execute()
    if response.data:
        for i, perfil in enumerate(response.data, start=1):
            print(f"{i}. Nome: {perfil['nome']} - Tipo: {perfil['tipo']}")


def criar_admin():
    """
    Cria um novo utilizador com perfil de administrador.

    Side Effects:
        - Pede inputs (nome, email, password) no terminal.
        - Faz `sign_up` e cria o registo em `perfil` com tipo `admin`.
        - Imprime feedback no terminal.
    """
    nome = input("Nome do admin: ")
    email = input("Email: ")
    password = input("Password: ")
    registar_utilizador(email, password, nome, "admin")


# Menu principal (interativo no topo do módulo)
print("Escolha o tipo de utilizador:")
print("1 -> Cliente")
print("2 -> Administrador")
tipo = int(input("Opção: "))

if tipo == 1:
    print("\nMenu Cliente")
    print("1 -> Registar")
    print("2 -> Fazer Login")
    funcao = int(input("Escolha a função: "))
    if funcao == 1:
        nome = input("Nome: ")
        email = input("Email: ")
        password = input("Password: ")
        registar_utilizador(email, password, nome, "cliente")
    elif funcao == 2:
        email = input("Email: ")
        password = input("Password: ")
        user = login_utilizador(email, password)
        if user:
            print(f"Bem-vindo, {email}")
        else:
            print("Credenciais inválidas.")

elif tipo == 2:
    print("\nLogin Administrador")
    email = input("Email: ")
    password = input("Password: ")
    user = login_utilizador(email, password)
    if user:
        perfil = supabase.table("perfil").select("tipo").eq("user_id", user.id).execute()
        if perfil.data and perfil.data[0]["tipo"] == "admin":
            print("\n Acesso autorizado ao menu de administração.")
            print("1 -> Listar utilizadores")
            print("2 -> Editar perfil")
            print("3 -> Remover perfil")
            funcao = int(input("Escolha a função: "))
            if funcao == 1:
                listar_utilizadores()
            elif funcao == 2:
                editar_perfil(user.id)
            elif funcao == 3:
                remover_perfil(user.id)
        else:
            print("Acesso negado. Não és administrador.")
    else:
        print("Credenciais inválidas.")