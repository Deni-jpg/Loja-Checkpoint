# 🛍️ Loja Checkpoint

Aplicação de loja digital em **terminal (CLI)** desenvolvida em **Python**, com base de dados no **Supabase**.  
O projeto simula uma loja de videojogos, onde utilizadores podem autenticar-se, comprar jogos, avaliar produtos, deixar comentários e muito mais — tudo diretamente no terminal.

## 🚀 Funcionalidades principais
- 🔐 **Login e registo de utilizadores**
- 🛒 **Sistema de carrinho e finalização de compras**
- 💬 **Comentários e moderação**
- ⭐ **Avaliação de produtos**
- 🆚 **Comparação de jogos com `tabulate`**
- ⚙️ **Configurações de tema (dark/light)**
- 🧑‍💼 **Gestão de utilizadores e produtos (admin)**

## 🗺️ Roadmap de desenvolvimento

| Estado | Funcionalidade             | Descrição                                      |
|:------:|----------------------------|-----------------------------------------------|
| ✅     | **Login e Registo**        | Sistema de autenticação via Supabase          |
| ✅     | **Carrinho e Compras**     | Adicionar, remover e finalizar compras        |
| ✅     | **Comentários**            | Clientes podem comentar produtos              |
| ✅     | **Avaliações**             | Sistema de 1 a 5 estrelas                      |
| ✅     | **Comparação de Jogos**    | Comparar produtos lado a lado no terminal     |
| 🧩     | **Wishlist (Lista de Desejos)** | Guardar jogos para comprar mais tarde    |
| 🧩     | **Histórico Detalhado**    | Mostrar compras com data e totais             |
| 🔜     | **Pontos de Fidelidade**   | Converter compras em pontos                   |
| 🔜     | **Painel Administrativo**  | CRUD de produtos e estatísticas               |
| 🔜     | **Promoções e Descontos**  | Preços promocionais no terminal               |
| 🔜     | **Exportação CSV**         | Exportar histórico e avaliações               |
| 🔜     | **Notificações Locais**    | Alertas de promoções e stock                  |
| 🔜     | **Sistema de Moderação**   | Aprovação de comentários por admin            |

> ✅ Concluído 🧩 Em progresso 🔜 Planeado

## ⚙️ Requisitos

- **Python 3.10+**
- **Dependências:** listadas no ficheiro `requirements.txt`

## 🧑‍💻 Como executar o projeto

```bash
git clone https://github.com/Deni-jpg/Loja-Checkpoint.git
cd Loja-Checkpoint
pip install -r requirements.txt
python main.py
```

## 🧩 Estrutura do projeto

 ├── main.py                # Menu global e lógica principal
 ├── auth.py                # Autenticação e registo de utilizadores
 ├── compras.py             # Lógica de compras e histórico
 ├── carrinho.py            # Carrinho de compras
 ├── produtos.py            # Gestão de produtos
 ├── produtos_utils.py      # Algumas funções produtos
 ├── clientes.py            # Perfil
 ├── comentarios.py         # Sistema de comentários
 ├── avaliacoes.py          # Avaliação por estrelas
 ├── comparar_jogos.py      # Comparação de jogos no terminal
 ├── notificacao_email.py   # Envio de emails via SendGrid
 ├── db.py                  # Ligação e instância Supabase
 ├── sessao.json            # Sessão do utilizador autenticado
 ├── config.json            # Configuração de tema
 └── .env                   # Credenciais do Supabase e SendGrid

 ## 💡 Próximas melhorias planeadas

- Implementar sistema de pontos e recompensas  
- Adicionar painel de administração no terminal  
– Mostrar estatísticas pessoais do cliente
- Criar exportação de dados em CSV  
- Adicionar sistema de notificações locais no login  
- Implementar gestão automática de stock e alertas no terminal
- Desenvolver sistema de promoções e descontos  

---

## 🧠 Tecnologias utilizadas

- **Python 3.10+**  
- **Supabase** — autenticação e base de dados  
- **SendGrid** — envio de notificações por email  
- **Tabulate** — tabelas formatadas no terminal  
- **Colorama** — cores e estilos no terminal  
- **Dotenv** — gestão de variáveis de ambiente  

---

## 👨‍💻 Autores

- **Deni-jpg**  
- **eduardo895**  
- **rodrigo14052005**  

---

📧 **Email:** [poisola42@gmail.com](mailto:poisola42@gmail.com)  
💼 **Projeto:** [Loja Checkpoint](https://github.com/Deni-jpg/Loja-Checkpoint)

