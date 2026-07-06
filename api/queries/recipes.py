from api.db import get_connection


def serialize_recipe_list_row(row):
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "category": row["category"],
        "inspiration_url": row["inspiration_url"],
        "created_at": row["created_at"].isoformat(),
        "current_version": row["current_version"],
    }


def serialize_ingredient_row(row):
    return {
        "id": str(row["id"]),
        "recipe_version_id": str(row["recipe_version_id"]),
        "name": row["name"],
        "amount": row["amount"],
        "amount_type": row["amount_type"],
        "created_at": row["created_at"].isoformat(),
    }


def serialize_recipe_version_row(row):
    return {
        "id": str(row["id"]),
        "recipe_id": str(row["recipe_id"]),
        "version_number": row["version_number"],
        "created_at": row["created_at"].isoformat(),
    }


def list_recipes():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                    r.id,
                    r.name,
                    r.category,
                    r.inspiration_url,
                    r.created_at,
                    coalesce(max(rv.version_number), 0) as current_version
                from recipes r
                left join recipe_versions rv on rv.recipe_id = r.id
                group by r.id
                order by r.created_at desc
                """
            )
            return [serialize_recipe_list_row(row) for row in cursor.fetchall()]


def get_recipe(recipe_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                    id,
                    name,
                    category,
                    inspiration_url,
                    created_at
                from recipes
                where id = %s
                """,
                (recipe_id,),
            )
            recipe = cursor.fetchone()

            if recipe is None:
                return None

            cursor.execute(
                """
                select
                    rv.id,
                    rv.recipe_id,
                    rv.version_number,
                    rv.created_at,
                    count(i.id) as ingredient_count
                from recipe_versions rv
                left join ingredients i on i.recipe_version_id = rv.id
                where rv.recipe_id = %s
                group by rv.id
                order by rv.version_number desc
                """,
                (recipe_id,),
            )
            versions = []
            for row in cursor.fetchall():
                version = serialize_recipe_version_row(row)
                version["ingredient_count"] = row["ingredient_count"]

                cursor.execute(
                    """
                    select
                        id,
                        recipe_version_id,
                        name,
                        amount,
                        amount_type,
                        created_at
                    from ingredients
                    where recipe_version_id = %s
                    order by created_at asc, id asc
                    """,
                    (row["id"],),
                )
                version["ingredients"] = [
                    serialize_ingredient_row(ingredient_row)
                    for ingredient_row in cursor.fetchall()
                ]
                versions.append(version)

    return {
        "id": str(recipe["id"]),
        "name": recipe["name"],
        "category": recipe["category"],
        "inspiration_url": recipe["inspiration_url"],
        "created_at": recipe["created_at"].isoformat(),
        "versions": versions,
    }


def create_recipe(name, category, inspiration_url):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into recipes (name, category, inspiration_url)
                values (%s, %s, %s)
                returning id, name, category, inspiration_url, created_at
                """,
                (name, category, inspiration_url),
            )
            recipe = cursor.fetchone()

            cursor.execute(
                """
                insert into recipe_versions (recipe_id, version_number)
                values (%s, 1)
                returning id, recipe_id, version_number, created_at
                """,
                (recipe["id"],),
            )
            version = cursor.fetchone()

        connection.commit()

    return {
        "recipe": {
            "id": str(recipe["id"]),
            "name": recipe["name"],
            "category": recipe["category"],
            "inspiration_url": recipe["inspiration_url"],
            "created_at": recipe["created_at"].isoformat(),
            "current_version": 1,
        },
        "version": serialize_recipe_version_row(version),
    }


def create_recipe_version(recipe_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select id
                from recipes
                where id = %s
                """,
                (recipe_id,),
            )
            recipe = cursor.fetchone()

            if recipe is None:
                return None, "recipe not found"

            cursor.execute(
                """
                select
                    id,
                    version_number
                from recipe_versions
                where recipe_id = %s
                order by version_number desc
                limit 1
                """,
                (recipe_id,),
            )
            latest_version = cursor.fetchone()
            latest_version_id = latest_version["id"] if latest_version else None
            next_version = latest_version["version_number"] + 1 if latest_version else 1

            cursor.execute(
                """
                insert into recipe_versions (recipe_id, version_number)
                values (%s, %s)
                returning id, recipe_id, version_number, created_at
                """,
                (recipe_id, next_version),
            )
            version = cursor.fetchone()

            if latest_version_id is not None:
                cursor.execute(
                    """
                    insert into ingredients (recipe_version_id, name, amount, amount_type)
                    select %s, name, amount, amount_type
                    from ingredients
                    where recipe_version_id = %s
                    order by created_at asc, id asc
                    """,
                    (version["id"], latest_version_id),
                )

        connection.commit()

    return serialize_recipe_version_row(version), None


def create_ingredient(recipe_id, name, amount, amount_type):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                    rv.id,
                    rv.recipe_id,
                    rv.version_number,
                    rv.created_at
                from recipe_versions rv
                where rv.recipe_id = %s
                order by rv.version_number desc
                limit 1
                """,
                (recipe_id,),
            )
            active_version = cursor.fetchone()

            if active_version is None:
                return None, "recipe not found"

            cursor.execute(
                """
                insert into ingredients (recipe_version_id, name, amount, amount_type)
                values (%s, %s, %s, %s)
                returning id, recipe_version_id, name, amount, amount_type, created_at
                """,
                (active_version["id"], name, amount, amount_type),
            )
            ingredient = cursor.fetchone()

        connection.commit()

    return {
        "ingredient": serialize_ingredient_row(ingredient),
        "active_version": serialize_recipe_version_row(active_version),
    }, None


def delete_recipe_version(recipe_id, version_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select count(*) as version_count
                from recipe_versions
                where recipe_id = %s
                """,
                (recipe_id,),
            )
            version_count = cursor.fetchone()["version_count"]

            if version_count <= 1:
                return "cannot delete the only version"

            cursor.execute(
                """
                delete from recipe_versions
                where id = %s and recipe_id = %s
                returning id
                """,
                (version_id, recipe_id),
            )
            deleted_version = cursor.fetchone()

            if deleted_version is None:
                return "version not found"

        connection.commit()

    return None
