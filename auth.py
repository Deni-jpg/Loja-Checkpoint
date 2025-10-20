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
            "tipo": tipo
        }).execute()
        print("Registo bem-sucedido.")
        return res.user
    else:
        print("Erro ao registar:", res)
        return None

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


# Logout
def logout_utilizador():
    supabase.auth.sign_out()
    print("Sessão terminada.")
