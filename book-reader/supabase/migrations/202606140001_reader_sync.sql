create table if not exists public.reading_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  book_id text not null,
  page_number integer not null check (page_number between 1 and 40),
  updated_at timestamptz not null default now(),
  primary key (user_id, book_id)
);

alter table public.reading_progress enable row level security;

drop policy if exists "Readers can view their own progress" on public.reading_progress;
create policy "Readers can view their own progress"
on public.reading_progress
for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "Readers can create their own progress" on public.reading_progress;
create policy "Readers can create their own progress"
on public.reading_progress
for insert
to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists "Readers can update their own progress" on public.reading_progress;
create policy "Readers can update their own progress"
on public.reading_progress
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create table if not exists public.book_entitlements (
  user_id uuid not null references auth.users(id) on delete cascade,
  book_id text not null,
  status text not null default 'active' check (status in ('active', 'refunded', 'revoked')),
  purchased_at timestamptz not null default now(),
  provider text,
  provider_payment_id text,
  primary key (user_id, book_id)
);

alter table public.book_entitlements enable row level security;

drop policy if exists "Readers can view their own book access" on public.book_entitlements;
create policy "Readers can view their own book access"
on public.book_entitlements
for select
to authenticated
using ((select auth.uid()) = user_id);

comment on table public.book_entitlements is
'Only a trusted payment webhook or server using the service role may create or update entitlements.';
