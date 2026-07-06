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


def serialize_instruction_row(row):
    return {
        "id": str(row["id"]),
        "recipe_version_id": str(row["recipe_version_id"]),
        "title": row["title"],
        "created_at": row["created_at"].isoformat(),
    }


def serialize_step_row(row):
    return {
        "id": str(row["id"]),
        "instruction_id": str(row["instruction_id"]),
        "step_number": row["step_number"],
        "body": row["body"],
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
                    and rv.deleted_at is null
                where r.deleted_at is null
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
                    and deleted_at is null
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
                    and rv.deleted_at is null
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

                cursor.execute(
                    """
                    select
                        id,
                        recipe_version_id,
                        title,
                        created_at
                    from instructions
                    where recipe_version_id = %s
                    order by created_at asc, id asc
                    """,
                    (row["id"],),
                )
                instructions = []
                for instruction_row in cursor.fetchall():
                    instruction = serialize_instruction_row(instruction_row)
                    cursor.execute(
                        """
                        select
                            id,
                            instruction_id,
                            step_number,
                            body,
                            created_at
                        from steps
                        where instruction_id = %s
                        order by step_number asc, created_at asc, id asc
                        """,
                        (instruction_row["id"],),
                    )
                    instruction["steps"] = [
                        serialize_step_row(step_row)
                        for step_row in cursor.fetchall()
                    ]
                    instructions.append(instruction)
                version["instructions"] = instructions
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


def populate_recipe_version_from_import(version_id, import_payload):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                delete from ingredients
                where recipe_version_id = %s
                """,
                (version_id,),
            )

            cursor.execute(
                """
                delete from instructions
                where recipe_version_id = %s
                """,
                (version_id,),
            )

            for ingredient in import_payload.get("ingredients", []):
                cursor.execute(
                    """
                    insert into ingredients (recipe_version_id, name, amount, amount_type)
                    values (%s, %s, %s, %s)
                    """,
                    (
                        version_id,
                        ingredient["name"],
                        ingredient["amount"],
                        ingredient["amount_type"],
                    ),
                )

            for instruction in import_payload.get("instructions", []):
                cursor.execute(
                    """
                    insert into instructions (recipe_version_id, title)
                    values (%s, %s)
                    returning id
                    """,
                    (version_id, instruction["title"]),
                )
                instruction_id = cursor.fetchone()["id"]

                for index, step_body in enumerate(instruction.get("steps", []), start=1):
                    cursor.execute(
                        """
                        insert into steps (instruction_id, step_number, body)
                        values (%s, %s, %s)
                        """,
                        (instruction_id, index, step_body),
                    )

        connection.commit()


def get_active_version(recipe_id):
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
                inner join recipes r on r.id = rv.recipe_id
                where rv.recipe_id = %s
                    and rv.deleted_at is null
                    and r.deleted_at is null
                order by rv.version_number desc
                limit 1
                """,
                (recipe_id,),
            )
            version = cursor.fetchone()

    if version is None:
        return None

    return serialize_recipe_version_row(version)


def create_recipe_version(recipe_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select id
                from recipes
                where id = %s
                    and deleted_at is null
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
                    and deleted_at is null
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

                cursor.execute(
                    """
                    select
                        id,
                        title
                    from instructions
                    where recipe_version_id = %s
                    order by created_at asc, id asc
                    """,
                    (latest_version_id,),
                )
                source_instructions = cursor.fetchall()

                for source_instruction in source_instructions:
                    cursor.execute(
                        """
                        insert into instructions (recipe_version_id, title)
                        values (%s, %s)
                        returning id
                        """,
                        (version["id"], source_instruction["title"]),
                    )
                    copied_instruction_id = cursor.fetchone()["id"]

                    cursor.execute(
                        """
                        insert into steps (instruction_id, step_number, body)
                        select %s, step_number, body
                        from steps
                        where instruction_id = %s
                        order by step_number asc, created_at asc, id asc
                        """,
                        (copied_instruction_id, source_instruction["id"]),
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
                inner join recipes r on r.id = rv.recipe_id
                where rv.recipe_id = %s
                    and rv.deleted_at is null
                    and r.deleted_at is null
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


def create_instruction(recipe_id, title):
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
                inner join recipes r on r.id = rv.recipe_id
                where rv.recipe_id = %s
                    and rv.deleted_at is null
                    and r.deleted_at is null
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
                insert into instructions (recipe_version_id, title)
                values (%s, %s)
                returning id, recipe_version_id, title, created_at
                """,
                (active_version["id"], title),
            )
            instruction = cursor.fetchone()

        connection.commit()

    serialized_instruction = serialize_instruction_row(instruction)
    serialized_instruction["steps"] = []
    return {
        "instruction": serialized_instruction,
        "active_version": serialize_recipe_version_row(active_version),
    }, None


def create_step(recipe_id, instruction_id, body):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                    i.id,
                    i.recipe_version_id
                from instructions i
                inner join recipe_versions rv on rv.id = i.recipe_version_id
                inner join recipes r on r.id = rv.recipe_id
                where i.id = %s and rv.recipe_id = %s
                    and rv.deleted_at is null
                    and r.deleted_at is null
                """,
                (instruction_id, recipe_id),
            )
            instruction = cursor.fetchone()

            if instruction is None:
                return None, "instruction not found"

            cursor.execute(
                """
                select coalesce(max(step_number), 0) + 1 as next_step_number
                from steps
                where instruction_id = %s
                """,
                (instruction_id,),
            )
            next_step_number = cursor.fetchone()["next_step_number"]

            cursor.execute(
                """
                insert into steps (instruction_id, step_number, body)
                values (%s, %s, %s)
                returning id, instruction_id, step_number, body, created_at
                """,
                (instruction_id, next_step_number, body),
            )
            step = cursor.fetchone()

        connection.commit()

    return {"step": serialize_step_row(step)}, None


def delete_recipe_version(recipe_id, version_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select count(*) as version_count
                from recipe_versions
                where recipe_id = %s
                    and deleted_at is null
                """,
                (recipe_id,),
            )
            version_count = cursor.fetchone()["version_count"]

            if version_count <= 1:
                return "cannot delete the only version"

            cursor.execute(
                """
                update recipe_versions
                set deleted_at = now()
                where id = %s and recipe_id = %s
                    and deleted_at is null
                returning id
                """,
                (version_id, recipe_id),
            )
            deleted_version = cursor.fetchone()

            if deleted_version is None:
                return "version not found"

        connection.commit()

    return None


def delete_recipe(recipe_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                update recipes
                set deleted_at = now()
                where id = %s
                    and deleted_at is null
                returning id
                """,
                (recipe_id,),
            )
            recipe = cursor.fetchone()

            if recipe is None:
                return "recipe not found"

            cursor.execute(
                """
                update recipe_versions
                set deleted_at = now()
                where recipe_id = %s
                    and deleted_at is null
                """,
                (recipe_id,),
            )

        connection.commit()

    return None
