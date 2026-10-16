grant select, insert, update, delete on public.app_storage to anon, authenticated;

notify pgrst, 'reload schema';
