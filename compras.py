from carrinho import (
    obter_ou_criar_carrinho,
    adicionar_item,
    listar_itens,
    remover_item,
    calcular_total,
    finalizar_carrinho
)
from produtos_utils import listar_produtos, obter_produto_por_id
from db import supabase
from pathlib import Path
import json
from datetime import datetime
from notificacao_email import enviar_email

SESSAO_PATH = Path(__file__).parent / "sessao.json"

def carregar_sessao():
    try:
        with open(SESSAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def notificar(mensagem, tipo="info"):
    cores = {
        "info": "\033[94m",
        "sucesso": "\033[92m",
        "erro": "\033[91m",
        "alerta": "\033[93m"
    }
    cor = cores.get(tipo, "\033[0m")
    print(f"{cor}🔔 {mensagem}\033[0m")

def recomendar_produto(user_id):
    response = supabase.table("compras").select("produto_id").eq("user_id", user_id).execute()
    comprados = [c["produto_id"] for c in response.data]

    if comprados:
        sugestao = comprados[-1]
        produto_resp = supabase.table("produtos").select("nome").eq("id", sugestao).execute()
        if produto_resp.data:
            nome = produto_resp.data[0]["nome"]
            notificar(f"💡 Já compraste {nome}. Queres ver produtos semelhantes?", "info")

def menu_compras():
    sessao = carregar_sessao()
    if not sessao:
        notificar("Precisas de fazer login primeiro.", "erro")
        return

    user_id = sessao["id"]
    tipo = sessao["tipo"]
    carrinho_id = obter_ou_criar_carrinho(user_id)

    recomendar_produto(user_id)

    while True:
        print("\n🛒 Menu de Compras")
        print("1. Ver produtos")
        print("2. Adicionar ao carrinho")
        print("3. Ver carrinho")
        print("4. Remover item")
        print("5. Finalizar compra")
        print("6. Ver histórico de compras")
        if tipo == "admin":
            print("7. 📊 Ver todas as compras (admin)")
            print("8. 🔝 Produtos mais comprados")
        print("0. Voltar")
        escolha = input("Escolha: ").strip()

        if escolha == "1":
            listar_produtos()

        elif escolha == "2":
            nome_busca = input("Digite parte do nome do jogo: ").strip()
            plataforma = input("Filtrar por plataforma (ou ENTER para todas): ").strip()

            query = supabase.table("produtos").select("*").ilike("nome", f"%{nome_busca}%")
            if plataforma:
                query = query.eq("plataforma", plataforma)

            response = query.order("preco", desc=False).execute()

            if not response.data:
                notificar("❌ Nenhum produto encontrado com esses critérios.", "erro")
                continue

            print("\n🔍 Produtos encontrados:")
            for i, produto in enumerate(response.data, start=1):
                print(f"{i}. {produto['nome']} ({produto['plataforma']}) - €{produto['preco']:.2f} | Stock: {produto['stock']}")

            try:
                escolha_produto = int(input("Escolha o número do produto: "))
                produto = response.data[escolha_produto - 1]
                quantidade = int(input("Quantidade: "))
                adicionar_item(carrinho_id, produto["id"], quantidade, produto["preco"])
                notificar(f"{produto['nome']} adicionado ao carrinho.", "sucesso")
                if produto["stock"] <= 5:
                    notificar("⚠️ Stock baixo para este produto!", "alerta")
            except (ValueError, IndexError):
                notificar("❌ Escolha inválida.", "erro")


        elif escolha == "3":
            itens = listar_itens(carrinho_id)
            if not itens:
                notificar("Carrinho vazio.", "info")
            else:
                print("\nItens no carrinho:")
                for item in itens:
                    print(f"{item['nome']} x{item['quantidade']} - €{item['total']:.2f}")
                print(f"Total: €{calcular_total(carrinho_id):.2f}")

        elif escolha == "4":
            produto_id = int(input("ID do produto a remover: "))
            remover_item(carrinho_id, produto_id)
            notificar("Item removido do carrinho.", "alerta")

        elif escolha == "5":
            finalizar_carrinho(carrinho_id, user_id)
            perfil = supabase.table("perfil").select("nome").eq("user_id", user_id).execute()
            
            if perfil.data and sessao.get("email"):
                nome = perfil.data[0]["nome"]
                email = sessao["email"]

                # Obter detalhes da compra
                itens = listar_itens(carrinho_id)
                total = calcular_total(carrinho_id)
                data_compra = datetime.now().strftime("%d/%m/%Y %H:%M")

                # Gerar corpo HTML do e-mail
                corpo_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2>Olá {nome},</h2>
                    <p>A tua compra foi concluída com sucesso em <b>{data_compra}</b>!</p>

                    <h3>🧾 Resumo da compra:</h3>
                    <table style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                        <tr style="background-color: #f2f2f2;">
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Produto</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Quantidade</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Preço Total</th>
                        </tr>
                        {''.join(f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{item['nome']}</td><td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{item['quantidade']}</td><td style='border: 1px solid #ddd; padding: 8px; text-align: right;'>€{item['total']:.2f}</td></tr>" for item in itens)}
                    </table>

                    <p style="margin-top: 20px; font-size: 1.1em;">
                        <b>Total: €{total:.2f}</b>
                    </p>

                    <p>Obrigado por comprar na <b>Loja Checkpoint</b>! 🎮</p>
                    <hr>
                    <p style="font-size: 0.9em; color: #777;">
                        Este e-mail foi enviado automaticamente. Não respondas a esta mensagem.
                    </p>
                </body>
                </html>
                """

                enviar_email(
                    destinatario=email,
                    nome=nome,
                    assunto="🧾 Confirmação da tua compra - Loja Checkpoint",
                    corpo_html=corpo_html
                )

            notificar("Compra finalizada com sucesso. Email enviado!", "sucesso")
            break


        elif escolha == "6":
            historico_compras(user_id)

        elif escolha == "7" and tipo == "admin":
            ver_todas_compras()

        elif escolha == "8" and tipo == "admin":
            produtos_mais_comprados()

        elif escolha == "0":
            break

        else:
            notificar("Opção inválida.", "erro")

def historico_compras(user_id):
    response = supabase.table("compras").select("produto_id", "data").eq("user_id", user_id).execute()
    compras = response.data

    if not compras:
        notificar("Ainda não fez nenhuma compra.", "info")
        return

    print("\n🧾 Histórico de compras:")
    for c in compras:
        produto_resp = supabase.table("produtos").select("nome").eq("id", c["produto_id"]).execute()
        nome = produto_resp.data[0]["nome"] if produto_resp.data else "Desconhecido"
        data_formatada = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
        print(f"{nome} - Comprado em: {data_formatada}")

def ver_todas_compras():
    response = supabase.table("compras").select("user_id", "produto_id", "data").execute()
    compras = response.data

    if not compras:
        notificar("Nenhuma compra registada.", "info")
        return

    print("\n📋 Todas as compras:")
    for c in compras:
        produto_resp = supabase.table("produtos").select("nome").eq("id", c["produto_id"]).execute()
        nome = produto_resp.data[0]["nome"] if produto_resp.data else "Desconhecido"
        data_formatada = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y %H:%M")
        print(f"User: {c['user_id']} - {nome} - {data_formatada}")

def produtos_mais_comprados():
    response = supabase.table("compras").select("produto_id").execute()
    compras = response.data

    if not compras:
        notificar("Nenhuma compra registada.", "info")
        return

    contagem = {}
    for c in compras:
        pid = c["produto_id"]
        contagem[pid] = contagem.get(pid, 0) + 1

    ordenado = sorted(contagem.items(), key=lambda x: x[1], reverse=True)

    print("\n🔝 Produtos mais comprados:")
    for pid, total in ordenado[:10]:
        produto_resp = supabase.table("produtos").select("nome").eq("id", pid).execute()
        nome = produto_resp.data[0]["nome"] if produto_resp.data else "Desconhecido"
        print(f"{nome} - {total} compras")

if __name__ == "__main__":
    menu_compras()
