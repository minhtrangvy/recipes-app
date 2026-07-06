create extension if not exists pgcrypto;

do $$
begin
    if not exists (
        select 1
        from pg_type
        where typname = 'recipe_category'
    ) then
        create type recipe_category as enum (
            'dessert',
            'main',
            'salad',
            'appetizer',
            'cocktail',
            'mocktail'
        );
    end if;
end
$$;

do $$
begin
    if not exists (
        select 1
        from pg_type
        where typname = 'ingredient_amount_type'
    ) then
        create type ingredient_amount_type as enum (
            'cup',
            'teaspoon',
            'tablespoon',
            'dash',
            'weight_g'
        );
    end if;
end
$$;

create table if not exists recipes (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    category recipe_category not null,
    inspiration_url text null,
    created_at timestamptz not null default now()
);

create table if not exists recipe_versions (
    id uuid primary key default gen_random_uuid(),
    recipe_id uuid not null references recipes(id) on delete cascade,
    version_number integer not null,
    created_at timestamptz not null default now(),
    unique (recipe_id, version_number)
);

create table if not exists ingredients (
    id uuid primary key default gen_random_uuid(),
    recipe_version_id uuid not null references recipe_versions(id) on delete cascade,
    name text not null,
    amount integer not null default 1,
    amount_type ingredient_amount_type not null default 'dash',
    created_at timestamptz not null default now()
);

alter table ingredients
    add column if not exists name text;

alter table ingredients
    add column if not exists amount integer;

alter table ingredients
    add column if not exists amount_type ingredient_amount_type;

alter table ingredients
    add column if not exists created_at timestamptz not null default now();

update ingredients
set name = 'ingredient'
where name is null;

update ingredients
set amount = 1
where amount is null;

update ingredients
set amount_type = 'dash'
where amount_type is null;

alter table ingredients
    alter column name set not null;

alter table ingredients
    alter column amount set not null;

alter table ingredients
    alter column amount_type set not null;
