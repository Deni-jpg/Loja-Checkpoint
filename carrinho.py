from datetime import datetime
from notificacao_email import enviar_email
from db import supabase
from ui import cabecalho, rodape, limpar_terminal, animar_carregamento
from colorama import Fore, Style
from tabulate import tabulate
from pathlib import Path
import json
import time

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
    print(f"{cores.get(tipo, Fore.WHITE)}🔔 {msg}{Style.RESET_ALL}")

# === Carrinho base ===
def obter_ou_criar_carrinho(user_id):
    animar_carregamento("A verificar carrinho ativo...")
    resp = (
        supabase.table("carrinhos")
        .select("id")
        .eq("user_id", user_id)
        .eq("ativo", True)
        .execute()
    )
    if resp.data:
        return resp.data[0]["id"]

    novo = supabase.table("carrinhos").insert({"user_id": user_id, "ativo": True}).execute()
    return novo.data[0]["id"]

def adicionar_item(carrinho_id, produto_id, quantidade, preco_unitario):
    supabase.table("itens_carrinho").insert({
        "carrinho_id": carrinho_id,
        "produto_id": produto_id,
        "quantidade": quantidade,
        "preco_unitario": preco_unitario
    }).execute()

def listar_itens(carrinho_id):
    animar_carregamento("A carregar itens do carrinho...")
    resp = (
        supabase.table("itens_carrinho")
        .select("produto_id, quantidade, preco_unitario")
        .eq("carrinho_id", carrinho_id)
        .execute()
    )
    itens = resp.data or []
    lista = []
    for item in itens:
        produto_resp = supabase.table("produtos").select("nome").eq("id", item["produto_id"]).execute()
        nome = produto_resp.data[0]["nome"] if produto_resp.data else "Desconhecido"
        lista.append({
            "nome": nome,
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
            "total": item["quantidade"] * item["preco_unitario"]
        })
    return lista

def remover_item(carrinho_id, produto_id):
    supabase.table("itens_carrinho").delete().eq("carrinho_id", carrinho_id).eq("produto_id", produto_id).execute()

def calcular_total(carrinho_id):
    resp = supabase.table("itens_carrinho").select("quantidade, preco_unitario").eq("carrinho_id", carrinho_id).execute()
    return sum(item["quantidade"] * item["preco_unitario"] for item in (resp.data or []))

def finalizar_carrinho(carrinho_id, user_id):
    # Obtém os itens do carrinho
    resp = supabase.table("itens_carrinho").select("produto_id, quantidade").eq("carrinho_id", carrinho_id).execute()
    itens = resp.data or []
    if not itens:
        notificar("❌ O carrinho está vazio.", "erro")
        return

    animar_carregamento("A finalizar compra...")

    # Carrega dados do utilizador (apenas perfil)
    perfil_resp = supabase.table("perfil").select("nome").eq("user_id", user_id).execute()
    nome = perfil_resp.data[0]["nome"] if perfil_resp.data else "Utilizador"

    # Monta tabela HTML dos produtos (mesmo que não envies por email)
    tabela_html = ""
    total = 0

    for item in itens:
        prod_resp = supabase.table("produtos").select("nome, preco, plataforma").eq("id", item["produto_id"]).execute()
        if not prod_resp.data:
            continue

        p = prod_resp.data[0]
        subtotal = p["preco"] * item["quantidade"]
        total += subtotal

        # insere compra individual
        for _ in range(item["quantidade"]):
            supabase.table("compras").insert({
                "user_id": user_id,
                "produto_id": item["produto_id"],
                "data": datetime.now().isoformat()
            }).execute()

        tabela_html += f"""
            <tr style="text-align:center;">
                <td>{p['nome']}</td>
                <td>{p['plataforma']}</td>
                <td>{item['quantidade']}</td>
                <td>€{p['preco']:.2f}</td>
                <td>€{subtotal:.2f}</td>
            </tr>
        """

    # Fecha o carrinho
    supabase.table("carrinhos").update({"ativo": False}).eq("id", carrinho_id).execute()

    # Mostra resumo no terminal
    limpar_terminal()
    cabecalho("Compra Finalizada", utilizador=nome)
    print(Fore.GREEN + "✅ Compra finalizada com sucesso!\n" + Style.RESET_ALL)

    print(tabulate(
        [
            [p["nome"], p["plataforma"], item["quantidade"], f"€{p['preco']:.2f}", f"€{p['preco'] * item['quantidade']:.2f}"]
            for item in itens
            for p in supabase.table("produtos").select("nome, plataforma, preco").eq("id", item["produto_id"]).execute().data
        ],
        headers=["Produto", "Plataforma", "Qtd", "Preço Unit.", "Total"],
        tablefmt="fancy_grid"
    ))

    print(f"\n💰 Total pago: {Fore.YELLOW}€{total:.2f}{Style.RESET_ALL}")
    print(f"🕒 Data da compra: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    rodape(utilizador=nome)
    notificar("🛒 Compra registada na tua conta!", "sucesso")

# === Histórico de compras ===
def historico_compras(user_id, nome):
    limpar_terminal()
    cabecalho("Histórico de Compras", utilizador=nome)

    animar_carregamento("A carregar histórico...")
    resp = (
        supabase.table("compras")
        .select("produto_id, data")
        .eq("user_id", user_id)
        .order("data", desc=True)
        .execute()
    )

    compras = resp.data or []
    if not compras:
        notificar("📭 Ainda não fizeste nenhuma compra.", "info")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    tabela = []
    total_gasto = 0
    for c in compras:
        prod = supabase.table("produtos").select("nome, preco, plataforma").eq("id", c["produto_id"]).execute()
        if not prod.data:
            continue
        p = prod.data[0]
        total_gasto += p["preco"]
        data = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
        tabela.append([p["nome"], p["plataforma"], f"€{p['preco']:.2f}", data])

    print(Fore.CYAN + "\n🧾 Histórico de Compras" + Style.RESET_ALL)
    print(tabulate(tabela, headers=["Produto", "Plataforma", "Preço", "Data"], tablefmt="fancy_grid"))
    print(f"\n💰 Total gasto: {Fore.YELLOW}€{total_gasto:.2f}{Style.RESET_ALL}")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")

def historico_detalhado(user_id, nome):
    limpar_terminal()
    cabecalho("Histórico Detalhado", utilizador=nome)

    animar_carregamento("A carregar detalhes de compra...")
    resp = (
        supabase.table("compras")
        .select("produto_id, data")
        .eq("user_id", user_id)
        .order("data", desc=True)
        .execute()
    )

    compras = resp.data or []
    if not compras:
        notificar("📭 Ainda não fizeste nenhuma compra.", "info")
        rodape(utilizador=nome)
        input("\nENTER para voltar...")
        return

    agrupado = {}
    for c in compras:
        pid = c["produto_id"]
        agrupado[pid] = agrupado.get(pid, 0) + 1

    tabela = []
    total_gasto = 0
    for pid, qtd in agrupado.items():
        p = supabase.table("produtos").select("nome, preco, plataforma").eq("id", pid).execute().data
        if not p:
            continue
        prod = p[0]
        subtotal = prod["preco"] * qtd
        total_gasto += subtotal
        tabela.append([prod["nome"], prod["plataforma"], qtd, f"€{prod['preco']:.2f}", f"€{subtotal:.2f}"])

    print(Fore.MAGENTA + "\n📦 Histórico Detalhado de Compras\n" + Style.RESET_ALL)
    print(tabulate(tabela, headers=["Produto", "Plataforma", "Qtd", "Preço Unit.", "Subtotal"], tablefmt="fancy_grid"))
    print(f"\n💰 Total gasto: {Fore.YELLOW}€{total_gasto:.2f}{Style.RESET_ALL}")

    rodape(utilizador=nome)
    input("\nENTER para voltar...")

# === Interface ===
def menu_compras():
    sessao = carregar_sessao()
    if not sessao:
        limpar_terminal()
        cabecalho("Carrinho")
        notificar("⛔ Precisas de fazer login para aceder às compras.", "erro")
        rodape()
        input("\nENTER para voltar...")
        return

    user_id = sessao["id"]
    nome = sessao["nome"]

    while True:
        limpar_terminal()
        cabecalho("Carrinho de Compras", utilizador=nome)

        print(Fore.MAGENTA + "🛒 Menu de Compras" + Style.RESET_ALL)
        print("-" * 50)
        print("1️⃣  Adicionar produto ao carrinho")
        print("2️⃣  Ver carrinho atual")
        print("3️⃣  Remover item")
        print("4️⃣  Finalizar compra")
        print("5️⃣  Ver histórico simples")
        print("6️⃣  Ver histórico detalhado")
        print("0️⃣  Voltar")
        escolha = input("\n👉 Escolha uma opção: ").strip()

        carrinho_id = obter_ou_criar_carrinho(user_id)

        if escolha == "1":
            termo = input("🔍 Digite parte do nome do produto: ").strip()
            animar_carregamento("A procurar produtos...")
            produtos = (
                supabase.table("produtos")
                .select("id, nome, preco, plataforma")
                .ilike("nome", f"%{termo}%")
                .execute()
                .data
            )

            if not produtos:
                notificar("❌ Nenhum produto encontrado.", "erro")
                input("\nENTER para voltar...")
                continue

            print("\n📋 Produtos encontrados:")
            for i, p in enumerate(produtos, start=1):
                print(f"{i}. {p['nome']} ({p['plataforma']}) - €{p['preco']:.2f}")

            try:
                idx = int(input("\nEscolha o número do produto: ")) - 1
                produto = produtos[idx]
                qtd = int(input("Quantidade: "))
                adicionar_item(carrinho_id, produto["id"], qtd, produto["preco"])
                notificar(f"✅ {produto['nome']} adicionado ao carrinho.", "sucesso")
            except Exception:
                notificar("❌ Erro ao adicionar produto.", "erro")
            input("\nENTER para continuar...")

        elif escolha == "2":
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

        elif escolha == "3":
            itens = listar_itens(carrinho_id)
            if not itens:
                notificar("🛒 Carrinho vazio.", "info")
                input("\nENTER para voltar...")
                continue

            print("\nItens no carrinho:")
            for i, item in enumerate(itens, start=1):
                print(f"{i}. {item['nome']} ({item['quantidade']}x)")

            termo = input("\nDigite parte do nome do produto a remover: ").strip()
            animar_carregamento("A remover item...")
            produto_resp = supabase.table("produtos").select("id").ilike("nome", f"%{termo}%").execute()
            if not produto_resp.data:
                notificar("❌ Produto não encontrado.", "erro")
                input("\nENTER para voltar...")
                continue

            remover_item(carrinho_id, produto_resp.data[0]["id"])
            notificar("🗑️ Produto removido do carrinho.", "alerta")
            input("\nENTER para voltar...")

        elif escolha == "4":
            finalizar_carrinho(carrinho_id, user_id)
            input("\nENTER para voltar...")

        elif escolha == "5":
            historico_compras(user_id, nome)

        elif escolha == "6":
            historico_detalhado(user_id, nome)

        elif escolha == "0":
            break

        else:
            notificar("❌ Opção inválida.", "erro")
            input("\nENTER para continuar...")

# === Execução direta ===
if __name__ == "__main__":
    menu_compras()
