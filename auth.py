"""
Autenticação e gestão básica de perfil via Supabase.

Este módulo centraliza:
- criação de cliente Supabase,
- registo de utilizadores,
- login (utilizador/admin),
- recuperação de palavra-passe,
- atualização de perfil,
- e logout.

Requer variáveis de ambiente:
    SUPABASE_URL, SUPABASE_KEY
Carregadas via `python-dotenv` (se houver `.env`).
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Configuração Supabase
supabase: Client = create_client(url, key)


# Registar utilizador
def registar_utilizador(email: str, password: str, nome: str, tipo: str):
    """
    Regista um novo utilizador no Supabase e cria o registo correspondente em `perfil`.

    Args:
        email (str): Email do utilizador.
        password (str): Palavra-passe.
        nome (str): Nome a ser guardado no perfil.
        tipo (str): Tipo de utilizador (ex.: 'cliente', 'admin').

    Returns:
        Any | None: Objeto `user` devolvido pelo Supabase em caso de sucesso; `None` se falhar.

    Side Effects:
        - Chama `auth.sign_up`.
        - Insere registo na tabela `perfil` (campos: `user_id`, `nome`, `tipo`, `email`).
        - Imprime mensagens no terminal.
    """
    res = supabase.auth.sign_up({"email": email, "password": password})
    if res.user:
        # Guardar dados adicionais no perfil
        supabase.table("perfil").insert({
            "user_id": res.user.id,
            "nome": nome,
            "tipo": tipo,
            "email": email
        }).execute()
        print("Registo bem-sucedido.")
        return res.user
    else:
        print("Erro ao registar:", res)
        return None


def recuperar_password(email: str):
    """
    Envia email de recuperação de palavra-passe.

    Args:
        email (str): Email do utilizador.

    Returns:
        None

    Side Effects:
        - Chama `auth.reset_password_email`.
        - Imprime mensagens de sucesso/erro no terminal.
    """
    try:
        supabase.auth.reset_password_email(email)
        print("Email de recuperação enviado com sucesso.")
    except Exception as e:
        print("Erro ao enviar email de recuperação:", str(e))


def atualizar_perfil(user_id: str, nome: str = None, tipo: str = None):
    """
    Atualiza campos opcionais do perfil de um utilizador.

    Args:
        user_id (str): ID do utilizador no Supabase.
        nome (str, optional): Novo nome a guardar.
        tipo (str, optional): Novo tipo (ex.: 'cliente', 'admin').

    Returns:
        None

    Side Effects:
        - Atualiza a tabela `perfil` com `update(...)`.
        - Imprime mensagens de sucesso/erro no terminal.
    """
    dados = {}
    if nome:
        dados["nome"] = nome
    if tipo:
        dados["tipo"] = tipo
    try:
        supabase.table("perfil").update(dados).eq("user_id", user_id).execute()
        print("Perfil atualizado com sucesso.")
    except Exception as e:
        print("Erro ao atualizar perfil:", str(e))


# Login
def login_utilizador(email: str, password: str):
    """
    Realiza login de um utilizador com email e palavra-passe.

    Args:
        email (str): Email de login.
        password (str): Palavra-passe.

    Returns:
        Any | None: Objeto `user` da sessão em caso de sucesso; `None` se falhar.

    Side Effects:
        - Chama `auth.sign_in_with_password`.
        - Imprime mensagens de sucesso/erro ou conta não verificada.
    """
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            print("Login bem-sucedido.")
            return res.session.user
        else:
            print("Credenciais inválidas.")
            return None
    except Exception as e:
        mensagem = str(e)
        if "Email not confirmed" in mensagem or "Email not verified" in mensagem:
            print("A tua conta ainda não está verificada. Verifica o email antes de fazer login.")
        else:
            print("Erro ao fazer login:", mensagem)
        return None


def login_admin(email: str, password: str):
    """
    Realiza login de um administrador com email e palavra-passe.

    Nota: a validação de que o utilizador é realmente admin deve ocorrer via
    tabela `perfil` (campo `tipo`), fora desta função.

    Args:
        email (str): Email.
        password (str): Palavra-passe.

    Returns:
        Any | None: Objeto `user` da sessão em caso de sucesso; `None` se falhar.

    Side Effects:
        - Chama `auth.sign_in_with_password`.
        - Imprime mensagens de sucesso/erro ou conta não verificada.
    """
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            print("Login bem-sucedido.")
            return res.session.user
        else:
            print("Credenciais inválidas.")
            return None
    except Exception as e:
        mensagem = str(e)
        if "Email not confirmed" in mensagem or "Email not verified" in mensagem:
            print("A tua conta ainda não está verificada. Verifica o email antes de fazer login.")
        else:
            print("Erro ao fazer login:", mensagem)
        return None


# Logout
def logout_utilizador():
    """
    Encerra a sessão de autenticação atual.

    Returns:
        None

    Side Effects:
        - Chama `auth.sign_out`.
        - Imprime confirmação no terminal.
    """
    supabase.auth.sign_out()
    print("Sessão terminada.")