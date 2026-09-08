create table if not exists public.app_storage (
  key text primary key,
  value jsonb not null,
  shared boolean not null default false,
  owner_id uuid references auth.users(id) on delete cascade,
  updated_at timestamptz not null default now(),
  constraint app_storage_owner_check
    check ((shared and owner_id is null) or (not shared and owner_id is not null))
);

alter table public.app_storage enable row level security;

create policy "shared storage is readable"
  on public.app_storage for select
  using (shared = true or owner_id = auth.uid());

create policy "authenticated storage is writable"
  on public.app_storage for insert
  with check (owner_id = auth.uid() or shared = true);

create policy "authenticated storage is updateable"
  on public.app_storage for update
  using (owner_id = auth.uid() or shared = true)
  with check (owner_id = auth.uid() or shared = true);

create policy "authenticated storage is deletable"
  on public.app_storage for delete
  using (owner_id = auth.uid() or shared = true);

create index if not exists app_storage_shared_key_idx
  on public.app_storage (shared, key);
