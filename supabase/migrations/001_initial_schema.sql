create extension if not exists pgcrypto;

create type public.product_type as enum (
  'pcb_basic',
  'pcb_bundle',
  'pcb_compatibility'
);

create type public.order_status as enum (
  'pending',
  'paid',
  'generated',
  'failed',
  'refunded'
);

create type public.payment_status as enum (
  'pending',
  'succeeded',
  'canceled',
  'refunded'
);

create table public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null unique,
  created_at timestamptz not null default now()
);

create table public.orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  product_type public.product_type not null,
  status public.order_status not null default 'pending',
  amount integer not null check (amount >= 0),
  input_data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.books (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null unique references public.orders(id) on delete cascade,
  user_id uuid not null references public.users(id) on delete cascade,
  html_url text not null,
  subject_name text not null,
  expires_at timestamptz,
  created_at timestamptz not null default now()
);

create table public.payments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references public.orders(id) on delete cascade,
  provider text not null default 'yookassa',
  provider_id text not null,
  status public.payment_status not null default 'pending',
  amount integer not null check (amount >= 0),
  paid_at timestamptz,
  created_at timestamptz not null default now(),
  unique (provider, provider_id)
);

create table public.chart_data (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  input_hash text not null,
  raw_json jsonb not null,
  patterns_json jsonb,
  created_at timestamptz not null default now(),
  unique (user_id, input_hash)
);

create index orders_user_id_created_at_idx on public.orders (user_id, created_at desc);
create index books_user_id_created_at_idx on public.books (user_id, created_at desc);
create index payments_order_id_idx on public.payments (order_id);
create index chart_data_user_id_input_hash_idx on public.chart_data (user_id, input_hash);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger orders_set_updated_at
before update on public.orders
for each row execute function public.set_updated_at();

alter table public.users enable row level security;
alter table public.orders enable row level security;
alter table public.books enable row level security;
alter table public.payments enable row level security;
alter table public.chart_data enable row level security;

create policy "Users can read own profile"
on public.users for select
using (auth.uid() = id);

create policy "Users can read own orders"
on public.orders for select
using (auth.uid() = user_id);

create policy "Users can read own books"
on public.books for select
using (auth.uid() = user_id);

create policy "Users can read own chart cache"
on public.chart_data for select
using (auth.uid() = user_id);

create policy "Users can read own payments"
on public.payments for select
using (
  exists (
    select 1
    from public.orders
    where orders.id = payments.order_id
      and orders.user_id = auth.uid()
  )
);

insert into storage.buckets (id, name, public)
values ('books', 'books', false)
on conflict (id) do nothing;

create policy "Users can read own stored books"
on storage.objects for select
using (
  bucket_id = 'books'
  and auth.uid()::text = (storage.foldername(name))[1]
);
