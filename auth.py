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
    try:
        supabase.auth.reset_password_email(email)
        print("Email de recuperação enviado com sucesso.")
    except Exception as e:
        print("Erro ao enviar email de recuperação:", str(e))
        

def atualizar_perfil(user_id: str, nome: str = None, tipo: str = None):
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
    supabase.auth.sign_out()
    print("Sessão terminada.")
