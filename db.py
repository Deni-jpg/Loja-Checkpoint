"""
Módulo de ligação à base de dados Supabase.

Este módulo:
- Carrega variáveis de ambiente definidas no ficheiro ``.env``.
- Valida a existência das credenciais necessárias.
- Cria e expõe um cliente Supabase para uso em todo o projeto.

A conexão é estabelecida através do SDK oficial do Supabase
(``supabase-py``), permitindo operações como:
seleções, inserções, atualizações e eliminações nas tabelas remotas.

Raises:
    Exception: Se as variáveis de ambiente ``SUPABASE_URL`` ou
    ``SUPABASE_KEY`` não estiverem definidas, impedindo a ligação
    à base de dados.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
"""str: URL do projeto Supabase carregada do ``.env``."""

key = os.getenv("SUPABASE_KEY")
"""str: Chave de API do Supabase carregada do ``.env``."""

if not url or not key:
    raise Exception("Credenciais do Supabase em falta no .env")

#: Instância global do cliente Supabase utilizada pelo restante projeto.
supabase: Client = create_client(url, key)
