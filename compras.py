from carrinho import (
    obter_ou_criar_carrinho,
    adicionar_item,
    listar_itens,
    remover_item,
    calcular_total,
    finalizar_carrinho
)
from produtos_utils import listar_produtos
from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from pathlib import Path
from datetime import datetime
from notificacao_email import enviar_email
from tabulate import tabulate
import json
import sys
import historico_compras as hist

SESSAO_PATH = Path(__file__).parent / "sessao.json"

# === Sessão ===
def carregar_sessao():
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# === Notificação colorida ===
def notificar(msg, tipo="info"):
    cores = {
        "info": Fore.CYAN,
        "sucesso": Fore.GREEN,
        "erro": Fore.RED,
        "alerta": Fore.YELLOW
    }
    icones = {
        "info": "ℹ️",
        "sucesso": "✅",
        "erro": "❌",
        "alerta": "⚠️"
    }
    print(f"{cores.get(tipo, Fore.WHITE)}{icones.get(tipo, '💬')} {msg}{Style.RESET_ALL}")

# === Helpers de entrada numérica (preço) ===
def _parse_float_pt(valor_str: str):
    """
    Aceita '9.99' ou '9,99' e devolve float. Retorna None se inválido.
    """
    try:
        return float(str(valor_str).replace(",", ".").strip())
    except Exception:
        return None

def _input_preco_opcional(prompt: str):
    """
    Lê um preço opcional (ENTER = None). Valida número >= 0.
    """
    while True:
        bruto = input(prompt).strip()
        if not bruto:
            return None
        v = _parse_float_pt(bruto)
        if v is None or v < 0:
            notificar("Preço inválido. Usa formato 19,99 ou 19.99 e valor >= 0.", "erro")
            continue
        return v

# === Busca avançada + adicionar ao carrinho ===
def adicionar_via_busca_avancada(carrinho_id, user_id):
    """
    Busca avançada por produtos e permite adicionar um item ao carrinho.
    Filtros: nome (opcional), plataforma(s), preço min/max, ordenação.
    """
    print("\n🔎 Filtro avançado (ENTER = ignorar):")
    nome_busca = input("   • Nome contém: ").strip()
    plataformas_raw = input("   • Plataforma(s) (ex: ps4, ps5) [ENTER = todas]: ").strip()
    preco_min = _input_preco_opcional("   • Preço mínimo (€): ")
    preco_max = _input_preco_opcional("   • Preço máximo (€): ")

    ordenar_por = (input("   • Ordenar por [preco|nome|stock] (ENTER = preco): ").strip().lower() or "preco")
    ordenar_dir = (input("   • Direção [asc|desc] (ENTER = asc): ").strip().lower() or "asc")
    if ordenar_por not in {"preco", "nome", "stock"}:
        ordenar_por = "preco"
    desc_flag = (ordenar_dir == "desc")

    # Construção da query Supabase
    animar_carregamento("A procurar produtos...")
    query = supabase.table("produtos").select("*")
    if nome_busca:
        query = query.ilike("nome", f"%{nome_busca}%")

    # Plataforma: 1 ou várias (usa .eq ou .in_)
    if plataformas_raw:
        plataformas = [p.strip() for p in plataformas_raw.split(",") if p.strip()]
        if len(plataformas) == 1:
            query = query.eq("plataforma", plataformas[0])
        else:
            # supabase-py suporta .in_ para filtros "IN"
            query = query.in_("plataforma", plataformas)

    # Preço
    if preco_min is not None:
        query = query.gte("preco", preco_min)
    if preco_max is not None:
        query = query.lte("preco", preco_max)

    # Ordenação
    produtos = query.order(ordenar_por, desc=desc_flag).execute().data

    if not produtos:
        notificar("❌ Nenhum produto encontrado com esses filtros.", "erro")
        return

    tabela = [[i+1, p["nome"], p.get("plataforma", "-"), f"€{p['preco']:.2f}", p.get("stock", 0)]
              for i, p in enumerate(produtos)]
    print()
    print(tabulate(tabela, headers=["Nº", "Produto", "Plataforma", "Preço", "Stock"], tablefmt="fancy_grid"))

    # Escolha para adicionar
    try:
        idx = int(input("\nEscolhe o número do produto para adicionar (0 = cancelar): ").strip())
        if idx == 0:
            notificar("Operação cancelada.", "info")
            return
        produto = produtos[idx - 1]
        qtd = int(input("Quantidade: ").strip())
        if qtd <= 0:
            notificar("Quantidade deve ser > 0.", "erro")
            return

        adicionar_item(carrinho_id, produto["id"], qtd, produto["preco"])
        notificar(f"{produto['nome']} adicionado ao carrinho.", "sucesso")
        if produto.get("stock", 0) <= 5:
            notificar("⚠️ Stock baixo para este produto!", "alerta")
    except Exception:
        notificar("❌ Erro ao adicionar produto (índice ou quantidade inválidos).", "erro")

# === Recomendar produto ===
def recomendar_produto(user_id):
    response = supabase.table("compras").select("produto_id").eq("user_id", user_id).execute()
    comprados = [c["produto_id"] for c in response.data or []]
    if comprados:
        ultimo = comprados[-1]
        produto = supabase.table("produtos").select("nome").eq("id", ultimo).execute().data
        if produto:
            notificar(f"💡 Já compraste {produto[0]['nome']}. Vê produtos semelhantes!", "info")

# === Menu de compras ===
def menu_compras():
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Compras")
        notificar("⛔ Precisas de fazer login primeiro.", "erro")
        rodape()
        input("\nENTER para voltar...")
        return

    user_id = sessao["id"]
    tipo = sessao["tipo"]
    nome = sessao["nome"]

    carrinho_id = obter_ou_criar_carrinho(user_id)

    while True:
        limpar_terminal()
        cabecalho("Menu de Compras", utilizador=nome)
        print(Fore.MAGENTA + "🛒 Loja Checkpoint — Compras" + Style.RESET_ALL)
        print("-" * 50)
        print("1️⃣ Ver produtos disponíveis")
        print("2️⃣ Adicionar produto ao carrinho (simples ou avançado)")
        print("3️⃣ Ver carrinho")
        print("4️⃣ Remover item")
        print("5️⃣ Finalizar compra")
        print("6️⃣ Ver histórico simples")
        print("7️⃣ Ver histórico detalhado")
        if tipo == "admin":
            print("8️⃣ Ver todas as compras (admin)")
            print("9️⃣ Produtos mais comprados")
        print("0️⃣ Voltar")

        escolha = input("\n👉 Escolha uma opção: ").strip()

        if escolha == "1":
            listar_produtos()
            input("\nENTER para voltar...")

        elif escolha == "2":
            # NOVO: escolha entre busca simples (original) e avançada (nova)
            modo = input("\nBusca [S]imples ou [A]vançada? (S/A): ").strip().lower()
            if modo == "a":
                adicionar_via_busca_avancada(carrinho_id, user_id)
                input("\nENTER para voltar...")
            else:
                # === Fluxo original (busca simples por nome + plataforma) ===
                nome_busca = input("\n🔎 Nome do jogo: ").strip()
                plataforma = input("🎮 Plataforma (ENTER para todas): ").strip()
                animar_carregamento("A procurar produtos...")
                query = supabase.table("produtos").select("*").ilike("nome", f"%{nome_busca}%")
                if plataforma:
                    query = query.eq("plataforma", plataforma)
                produtos = query.order("preco").execute().data

                if not produtos:
                    notificar("❌ Nenhum produto encontrado.", "erro")
                    input("\nENTER para voltar...")
                    continue

                tabela = [[i+1, p["nome"], p["plataforma"], f"€{p['preco']:.2f}", p["stock"]] for i, p in enumerate(produtos)]
                print(tabulate(tabela, headers=["Nº", "Produto", "Plataforma", "Preço", "Stock"], tablefmt="fancy_grid"))
                try:
                    idx = int(input("\nEscolha o número do produto: ")) - 1
                    produto = produtos[idx]
                    qtd = int(input("Quantidade: "))
                    adicionar_item(carrinho_id, produto["id"], qtd, produto["preco"])
                    notificar(f"{produto['nome']} adicionado ao carrinho.", "sucesso")
                    if produto["stock"] <= 5:
                        notificar("⚠️ Stock baixo para este produto!", "alerta")
                except Exception:
                    notificar("❌ Erro ao adicionar produto.", "erro")
                input("\nENTER para continuar...")

        elif escolha == "3":
            itens = listar_itens(carrinho_id)
            limpar_terminal()
            cabecalho("Carrinho Atual", utilizador=nome)
            if not itens:
                notificar("🛒 O teu carrinho está vazio.", "info")
            else:
                tabela = [
                    [i["nome"], i["quantidade"], f"€{i['preco_unitario']:.2f}", f"€{i['total']:.2f}"]
                    for i in itens
                ]
                print(tabulate(tabela, headers=["Produto", "Qtd", "Preço Unit.", "Total"], tablefmt="fancy_grid"))
                print(f"\n💰 Total: {Fore.YELLOW}€{calcular_total(carrinho_id):.2f}{Style.RESET_ALL}")
            rodape(utilizador=nome)
            input("\nENTER para voltar...")

        elif escolha == "4":
            termo = input("\nProduto a remover: ").strip()
            produto_resp = supabase.table("produtos").select("id").ilike("nome", f"%{termo}%").execute()
            if not produto_resp.data:
                notificar("❌ Produto não encontrado.", "erro")
                input("\nENTER para voltar...")
                continue
            remover_item(carrinho_id, produto_resp.data[0]["id"])
            notificar("🗑️ Produto removido do carrinho.", "alerta")
            input("\nENTER para voltar...")

        elif escolha == "5":
            finalizar_carrinho(carrinho_id, user_id)
            notificar("✅ Compra finalizada com sucesso!", "sucesso")
            input("\nENTER para voltar...")
            break

        elif escolha == "6":
            historico_simples(user_id, nome)

        elif escolha == "7":
            hist.ver_historico_compras()

        elif escolha == "8" and tipo == "admin":
            ver_todas_compras(nome)

        elif escolha == "9" and tipo == "admin":
            produtos_mais_comprados(nome)

        elif escolha == "0":
            break

        else:
            notificar("❌ Opção inválida.", "erro")
            input("\nENTER para continuar...")

# === Histórico simples ===
def historico_simples(user_id, nome):
    limpar_terminal()
    cabecalho("Histórico de Compras", utilizador=nome)
    animar_carregamento("A carregar histórico...")
    compras = supabase.table("compras").select("produto_id, data").eq("user_id", user_id).execute().data
    if not compras:
        notificar("📭 Ainda não fizeste nenhuma compra.", "info")
    else:
        tabela = []
        for c in compras:
            produto = supabase.table("produtos").select("nome").eq("id", c["produto_id"]).execute().data
            if produto:
                data_fmt = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
                tabela.append([produto[0]["nome"], data_fmt])
        print(tabulate(tabela, headers=["Produto", "Data"], tablefmt="fancy_grid"))
    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === Admin: ver todas as compras ===
def ver_todas_compras(nome):
    limpar_terminal()
    cabecalho("Todas as Compras", utilizador=nome)
    animar_carregamento("A carregar compras...")
    compras = supabase.table("compras").select("user_id, produto_id, data").execute().data
    if not compras:
        notificar("📭 Nenhuma compra registada.", "info")
    else:
        tabela = []
        for c in compras:
            prod = supabase.table("produtos").select("nome").eq("id", c["produto_id"]).execute().data
            nome_p = prod[0]["nome"] if prod else "Desconhecido"
            data_fmt = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
            tabela.append([c["user_id"], nome_p, data_fmt])
        print(tabulate(tabela, headers=["Utilizador", "Produto", "Data"], tablefmt="fancy_grid"))
    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === Admin: produtos mais comprados ===
def produtos_mais_comprados(nome):
    limpar_terminal()
    cabecalho("Top Produtos", utilizador=nome)
    animar_carregamento("A calcular ranking...")
    compras = supabase.table("compras").select("produto_id").execute().data
    if not compras:
        notificar("📭 Nenhuma compra registada.", "info")
        return
    contagem = {}
    for c in compras:
        pid = c["produto_id"]
        contagem[pid] = contagem.get(pid, 0) + 1
    top = sorted(contagem.items(), key=lambda x: x[1], reverse=True)[:10]
    tabela = []
    for pid, total in top:
        produto = supabase.table("produtos").select("nome").eq("id", pid).execute().data
        nome_p = produto[0]["nome"] if produto else "Desconhecido"
        tabela.append([nome_p, total])
    print(tabulate(tabela, headers=["Produto", "Nº Compras"], tablefmt="fancy_grid"))
    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === Execução direta ===
if __name__ == "__main__":
    menu_compras()