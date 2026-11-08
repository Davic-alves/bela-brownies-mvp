# Bela Brownies MVP

Sistema web responsivo (mobile-first) para gestão de pedidos personalizados e
controle de estoque de insumos da confeitaria artesanal **Bela Brownies**
(Planaltina-DF). Projeto acadêmico de Análise e Desenvolvimento de Sistemas.

## Problema
Os pedidos chegam por WhatsApp e Instagram e são anotados à mão. Detalhes de
personalização se perdem e faltam insumos em datas de pico.

## Funcionalidades (MVP)
| Código | Requisito | Prioridade |
|---|---|---|
| RF01 | Cadastro de pedidos (cliente, descrição, data de entrega) | Obrigatório |
| RF02 | Controle de estoque de insumos | Obrigatório |
| RF03 | Baixa automática de insumos ao salvar o pedido (transação atômica) | Obrigatório |
| RF04 | Alerta visual (cor + ícone + texto) de estoque mínimo | Desejável |

Também inclui login (Argon2 + sessão JWT em cookie HttpOnly) e atualização de
status do pedido (pendente → em produção → pronto → entregue).

## Tecnologias
Python · FastAPI · Jinja2 · Tailwind CSS · Supabase (PostgreSQL)

## Estrutura
```
app/         rotas (main.py), banco (db.py), autenticação (security.py), config
templates/   telas HTML (login, menu, novo pedido, estoque)
static/      estilos
docs/        protótipos e documentação
schema.sql   tabelas e função criar_pedido (rodar no Supabase)
```

## Como executar
1. Crie um projeto no [Supabase](https://supabase.com) e rode `schema.sql` no SQL Editor.
2. Clone o repositório e crie o ambiente:
   ```bash
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. `cp .env.example .env` e preencha as chaves. Gere o hash da senha com:
   ```bash
   python -m app.security "sua-senha"
   ```
4. Rode: `uvicorn app.main:app --reload` e abra http://localhost:8000

## Segurança (resumo)
Senhas com Argon2 · sessão HttpOnly · consultas parametrizadas · validação no
servidor · limite de tentativas de login · segredos só em variáveis de ambiente ·
erros genéricos na tela.

## ODS
ODS 8 — Trabalho Decente e Crescimento Econômico.

## Status
Em desenvolvimento.
