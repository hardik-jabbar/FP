-- 0. Drop existing functions with CASCADE to remove dependent objects
drop function if exists public.handle_price_change() cascade;
drop function if exists public.update_favorites_count() cascade;

-- 1. Drop existing triggers if they still exist (in case CASCADE didn't work)
drop trigger if exists on_products_price_change on public.products;
drop trigger if exists on_favorites_change on public.favorites;

-- 1. Create the favorites table first
create table if not exists public.favorites (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  product_id bigint not null references public.products(id) on delete cascade,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(user_id, product_id)
);

-- 2. Create the price_history table
create table if not exists public.price_history (
  id bigserial primary key,
  product_id bigint not null references public.products(id) on delete cascade,
  previous_price integer not null,
  new_price integer not null,
  changed_by uuid references auth.users(id) on delete set null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Add favorites_count column to products if it doesn't exist
do $$
begin
  if not exists (select 1 from information_schema.columns 
                where table_schema = 'public' 
                and table_name = 'products' 
                and column_name = 'favorites_count') then
    alter table public.products
    add column favorites_count integer not null default 0;
  end if;
exception when others then
  raise notice 'Could not add favorites_count column: %', SQLERRM;
end $$;

-- 4. Create indexes for better performance
create index if not exists idx_favorites_user_id on public.favorites(user_id);
create index if not exists idx_favorites_product_id on public.favorites(product_id);
create index if not exists idx_favorites_user_product on public.favorites(user_id, product_id);
create index if not exists idx_price_history_product_id on public.price_history(product_id);

-- 5. Create or replace the update_favorites_count function
create or replace function public.update_favorites_count()
returns trigger as $$
begin
  if tg_op = 'DELETE' then
    update public.products
    set favorites_count = (
      select count(*) 
      from public.favorites 
      where product_id = old.product_id
    )
    where id = old.product_id;
    return old;
  else
    update public.products
    set favorites_count = (
      select count(*) 
      from public.favorites 
      where product_id = new.product_id
    )
    where id = new.product_id;
    return new;
  end if;
end;
$$ language plpgsql security definer;

-- 6. Create or replace the handle_price_change function
create or replace function public.handle_price_change()
returns trigger as $$
begin
  if new.price_cents != old.price_cents then
    insert into public.price_history (product_id, previous_price, new_price, changed_by)
    values (new.id, old.price_cents, new.price_cents, auth.uid());
  end if;
  return new;
end;
$$ language plpgsql security definer;

-- 7. Enable Row Level Security and create policies for favorites
do $$
begin
  if exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'favorites') then
    alter table public.favorites enable row level security;
    
    drop policy if exists "Enable read access for own favorites" on public.favorites;
    create policy "Enable read access for own favorites" 
    on public.favorites for select 
    using (auth.uid() = user_id);
    
    drop policy if exists "Enable insert for authenticated users only" on public.favorites;
    create policy "Enable insert for authenticated users only" 
    on public.favorites for insert 
    to authenticated 
    with check (true);
    
    drop policy if exists "Enable delete for own favorites" on public.favorites;
    create policy "Enable delete for own favorites" 
    on public.favorites for delete 
    using (auth.uid() = user_id);
  end if;
end $$;

-- 8. Enable Row Level Security and create policies for price_history
do $$
begin
  if exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'price_history') then
    alter table public.price_history enable row level security;
    
    drop policy if exists "Enable read access for all users" on public.price_history;
    create policy "Enable read access for all users" 
    on public.price_history for select 
    using (true);
    
    drop policy if exists "Enable insert for authenticated users only" on public.price_history;
    create policy "Enable insert for authenticated users only" 
    on public.price_history for insert 
    to authenticated 
    with check (true);
  end if;
end $$;

-- 9. Create or replace the search_products function
create or replace function public.search_products(
  p_search_term text default null,
  p_category_id bigint default null,
  p_min_price integer default null,
  p_max_price integer default null,
  p_sort_by text default 'created_at',
  p_sort_order text default 'desc',
  p_page integer default 1,
  p_page_size integer default 20
)
returns table (
  id bigint,
  title text,
  description text,
  price_cents integer,
  image_url text,
  category_id bigint,
  created_at timestamp with time zone,
  favorites_count integer,
  total_count bigint
) 
language plpgsql 
stable 
security invoker
as $$
declare
  v_offset integer := (p_page - 1) * p_page_size;
  v_sql text;
  v_where_conditions text[] := ARRAY['p.active = true'];
  v_params text[] := ARRAY[]::text[];
  v_param_count integer := 0;
  v_order_by text;
  v_limit_offset text;
begin
  -- Build WHERE conditions
  if p_category_id is not null then
    v_param_count := v_param_count + 1;
    v_where_conditions := array_append(v_where_conditions, 'p.category_id = $' || v_param_count::text);
    v_params := array_append(v_params, p_category_id::text);
  end if;

  if p_min_price is not null then
    v_param_count := v_param_count + 1;
    v_where_conditions := array_append(v_where_conditions, 'p.price_cents >= $' || v_param_count::text);
    v_params := array_append(v_params, p_min_price::text);
  end if;

  if p_max_price is not null then
    v_param_count := v_param_count + 1;
    v_where_conditions := array_append(v_where_conditions, 'p.price_cents <= $' || v_param_count::text);
    v_params := array_append(v_params, p_max_price::text);
  end if;

  if p_search_term is not null then
    v_param_count := v_param_count + 1;
    v_where_conditions := array_append(v_where_conditions, 
      '(p.title ilike $' || (v_param_count + 1)::text || 
      ' or p.description ilike $' || (v_param_count + 1)::text || ')'
    );
    v_params := array_append(v_params, '%' || p_search_term || '%');
  end if;

  -- Build ORDER BY
  v_order_by := 'order by ' || 
               quote_ident(p_sort_by) || ' ' || 
               case when lower(p_sort_order) = 'asc' then 'asc' else 'desc' end;

  -- Build LIMIT and OFFSET
  v_param_count := v_param_count + 1;
  v_limit_offset := 'limit $' || v_param_count::text;
  v_params := array_append(v_params, p_page_size::text);
  
  v_param_count := v_param_count + 1;
  v_limit_offset := v_limit_offset || ' offset $' || v_param_count::text;
  v_params := array_append(v_params, v_offset::text);

  -- Build the final query
  v_sql := 'with search_results as (
    select 
      p.*,
      count(*) over() as total_count
    from public.products p
    where ' || array_to_string(v_where_conditions, ' and ') || '
    ' || v_order_by || '
    ' || v_limit_offset || '
  )
  select 
    id,
    title,
    description,
    price_cents,
    image_url,
    category_id,
    created_at,
    coalesce(favorites_count, 0) as favorites_count,
    total_count
  from search_results';

  -- Execute the query with parameters
  if array_length(v_params, 1) > 0 then
    return query execute v_sql using v_params[1], v_params[2], v_params[3], v_params[4], v_params[5], v_params[6];
  else
    return query execute v_sql;
  end if;
end;
$$;

-- 10. Create or replace the triggers
drop trigger if exists on_products_price_change on public.products;
create trigger on_products_price_change
  after update of price_cents on public.products
  for each row
  when (old.price_cents is distinct from new.price_cents)
  execute function public.handle_price_change();

drop trigger if exists on_favorites_change on public.favorites;
create trigger on_favorites_change
  after insert or delete on public.favorites
  for each row
  execute function public.update_favorites_count();

-- 11. Update existing favorites count for all products
update public.products p
set favorites_count = (
  select count(*) 
  from public.favorites f 
  where f.product_id = p.id
);
