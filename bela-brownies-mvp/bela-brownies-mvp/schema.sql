-- Execute no SQL Editor do Supabase

create table insumos (
  id bigint generated always as identity primary key,
  nome_insumo text not null,
  quantidade_atual numeric not null default 0 check (quantidade_atual >= 0),
  unidade_medida text not null,
  limite_minimo numeric not null default 0 check (limite_minimo >= 0)
);

create table pedidos (
  id bigint generated always as identity primary key,
  cliente text not null,
  descricao text not null,
  data_entrega date not null,
  status text not null default 'pendente'
    check (status in ('pendente','em_producao','pronto','entregue')),
  criado_em timestamptz not null default now()
);

-- Quanto de cada insumo cada pedido consumiu (resolve a baixa automática)
create table pedido_itens (
  id bigint generated always as identity primary key,
  pedido_id bigint not null references pedidos(id) on delete cascade,
  insumo_id bigint not null references insumos(id),
  quantidade numeric not null check (quantidade > 0)
);

-- Cria o pedido e dá baixa no estoque na MESMA transação (RF03).
-- Se algum insumo ficar negativo, o CHECK falha e tudo é desfeito.
create or replace function criar_pedido(
  p_cliente text, p_descricao text, p_data_entrega date, p_itens jsonb
) returns bigint language plpgsql as $$
declare v_id bigint; item jsonb;
begin
  if p_data_entrega < current_date then
    raise exception 'A data de entrega não pode ser anterior a hoje.';
  end if;
  insert into pedidos(cliente, descricao, data_entrega)
    values (p_cliente, p_descricao, p_data_entrega) returning id into v_id;
  for item in select * from jsonb_array_elements(p_itens) loop
    insert into pedido_itens(pedido_id, insumo_id, quantidade)
      values (v_id, (item->>'insumo_id')::bigint, (item->>'quantidade')::numeric);
    update insumos
      set quantidade_atual = quantidade_atual - (item->>'quantidade')::numeric
      where id = (item->>'insumo_id')::bigint;
  end loop;
  return v_id;
end $$;

-- Só o backend (service key) acessa as tabelas
alter table insumos enable row level security;
alter table pedidos enable row level security;
alter table pedido_itens enable row level security;

-- Dados de exemplo
insert into insumos (nome_insumo, quantidade_atual, unidade_medida, limite_minimo) values
 ('Chocolate nobre', 12, 'kg', 3),
 ('Embalagem caixa P', 2, 'un', 10),
 ('Fita de cetim', 40, 'un', 10);
