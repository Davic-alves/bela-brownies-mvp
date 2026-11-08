# Bela Brownies MVP

Sistema web responsivo (mobile-first) para gestão de pedidos personalizados
e controle de estoque de insumos da confeitaria artesanal Bela Brownies,
em Planaltina-DF.

## Problema
Pedidos chegam por WhatsApp e Instagram e são anotados manualmente, o que
causa esquecimentos de personalização e falta de insumos em datas de pico.

## Funcionalidades do MVP
- RF01: Cadastro de pedidos (cliente, descrição, data de entrega)
- RF02: Controle de estoque de insumos
- RF03: Baixa automática de insumos ao cadastrar um pedido
- RF04: Alerta visual de estoque mínimo (desejável)

## Tecnologias
- Python + FastAPI
- Tailwind CSS
- Supabase (PostgreSQL)

## Estrutura do projeto
app/        código da aplicação (rotas, regras de negócio, acesso a dados)
templates/  telas HTML
static/     estilos e recursos estáticos
docs/       documentação e protótipos

## Como executar
1. Clone o repositório
2. Crie um ambiente virtual e instale as dependências:
   pip install -r requirements.txt
3. Copie `.env.example` para `.env` e preencha as chaves do Supabase
4. Execute: uvicorn app.main:app --reload

## ODS
ODS 8 - Trabalho Decente e Crescimento Econômico

## Status
Em desenvolvimento (projeto acadêmico de Análise e Desenvolvimento de Sistemas).
