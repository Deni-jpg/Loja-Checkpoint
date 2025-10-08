-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.admins (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome text NOT NULL,
  email text NOT NULL UNIQUE,
  password text NOT NULL,
  criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT admins_pkey PRIMARY KEY (id)
);
CREATE TABLE public.clientes (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome text NOT NULL,
  email text NOT NULL UNIQUE,
  password text NOT NULL,
  criado_em timestamp without time zone DEFAULT now(),
  CONSTRAINT clientes_pkey PRIMARY KEY (id)
);
CREATE TABLE public.comentarios (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  produto_id bigint,
  autor text,
  texto text,
  aprovado boolean DEFAULT true,
  CONSTRAINT comentarios_pkey PRIMARY KEY (id),
  CONSTRAINT comentarios_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id)
);
CREATE TABLE public.compras (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  cliente_id bigint,
  produto_id bigint,
  data timestamp without time zone DEFAULT now(),
  CONSTRAINT compras_pkey PRIMARY KEY (id),
  CONSTRAINT compras_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id)
);
CREATE TABLE public.produtos (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome text NOT NULL,
  plataforma text,
  preco numeric,
  stock integer,
  vendas integer DEFAULT 0,
  descricao text,
  CONSTRAINT produtos_pkey PRIMARY KEY (id)
);
CREATE TABLE public.wishlist (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  cliente_id bigint,
  produto_id bigint,
  adicionado_em timestamp without time zone DEFAULT now(),
  CONSTRAINT wishlist_pkey PRIMARY KEY (id),
  CONSTRAINT wishlist_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id)
);