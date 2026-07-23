-- Auth-independent persistence for the current MVP flow (no Supabase Auth yet).
-- Only the service role (server) reads/writes these tables: RLS is enabled with
-- no public policies, so the anon/public key cannot touch them.

create extension if not exists pgcrypto;

create table if not exists public.generation_orders (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  product text not null,
  amount integer not null default 0 check (amount >= 0),
  status text not null default 'demo',
  input_data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists generation_orders_email_idx
  on public.generation_orders (email, created_at desc);

create table if not exists public.generation_books (
  book_id text primary key,
  subject_name text,
  resolved_theme text,
  generated_with text,
  sections jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.generation_orders enable row level security;
alter table public.generation_books enable row level security;
-- No policies on purpose: only the service role bypasses RLS.
