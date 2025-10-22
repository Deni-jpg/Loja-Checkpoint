-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.comentarios (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  produto_id bigint,
  user_id uuid,
  texto text,
  aprovado boolean DEFAULT true,
  CONSTRAINT comentarios_pkey PRIMARY KEY (id),
  CONSTRAINT comentarios_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id),
  CONSTRAINT comentarios_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.compras (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id uuid,
  produto_id bigint,
  data timestamp without time zone DEFAULT now(),
  CONSTRAINT compras_pkey PRIMARY KEY (id),
  CONSTRAINT compras_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT compras_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id)
);
CREATE TABLE public.perfil (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  nome text NOT NULL,
  tipo text NOT NULL CHECK (tipo = ANY (ARRAY['cliente'::text, 'admin'::text])),
  criado_em timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT perfil_pkey PRIMARY KEY (id),
  CONSTRAINT perfil_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
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
  user_id uuid,
  produto_id bigint,
  adicionado_em timestamp without time zone DEFAULT now(),
  CONSTRAINT wishlist_pkey PRIMARY KEY (id),
  CONSTRAINT wishlist_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT wishlist_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id)
);