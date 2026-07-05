from flask import Flask, jsonify, request

from api.db import get_connection


CATEGORIES = (
    "dessert",
    "main",
    "salad",
    "appetizer",
    "cocktail",
    "mocktail",
)

app = Flask(__name__)


def serialize_recipe_list_row(row):
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "category": row["category"],
        "inspiration_url": row["inspiration_url"],
        "created_at": row["created_at"].isoformat(),
        "current_version": row["current_version"],
    }


def serialize_recipe_version_row(row):
    return {
        "id": str(row["id"]),
        "recipe_id": str(row["recipe_id"]),
        "version_number": row["version_number"],
        "created_at": row["created_at"].isoformat(),
    }


def validate_recipe_payload(payload):
    name = (payload.get("name") or "").strip()
    category = payload.get("category")
    inspiration_url = payload.get("inspiration_url")

    if not name:
        return None, ("name is required", 400)

    if category not in CATEGORIES:
        return None, ("category is invalid", 400)

    if inspiration_url == "":
        inspiration_url = None

    return {
        "name": name,
        "category": category,
        "inspiration_url": inspiration_url,
    }, None


@app.get("/api/health")
def healthcheck():
    return {"ok": True}


@app.get("/api/recipes")
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
            recipes = [serialize_recipe_list_row(row) for row in cursor.fetchall()]

    return jsonify({"recipes": recipes})


@app.get("/api/recipes/<recipe_id>")
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
                return {"error": "recipe not found"}, 404

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
                versions.append(version)

    return jsonify(
        {
            "recipe": {
                "id": str(recipe["id"]),
                "name": recipe["name"],
                "category": recipe["category"],
                "inspiration_url": recipe["inspiration_url"],
                "created_at": recipe["created_at"].isoformat(),
                "versions": versions,
            }
        }
    )


@app.post("/api/recipes")
def create_recipe():
    payload, error = validate_recipe_payload(request.get_json(silent=True) or {})
    if error is not None:
        message, status_code = error
        return {"error": message}, status_code

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into recipes (name, category, inspiration_url)
                values (%s, %s, %s)
                returning id, name, category, inspiration_url, created_at
                """,
                (
                    payload["name"],
                    payload["category"],
                    payload["inspiration_url"],
                ),
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

    return (
        jsonify(
            {
                "recipe": {
                    "id": str(recipe["id"]),
                    "name": recipe["name"],
                    "category": recipe["category"],
                    "inspiration_url": recipe["inspiration_url"],
                    "created_at": recipe["created_at"].isoformat(),
                },
                "version": serialize_recipe_version_row(version),
            }
        ),
        201,
    )


@app.post("/api/recipes/<recipe_id>/versions")
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
                return {"error": "recipe not found"}, 404

            cursor.execute(
                """
                select coalesce(max(version_number), 0) + 1 as next_version
                from recipe_versions
                where recipe_id = %s
                """,
                (recipe_id,),
            )
            next_version = cursor.fetchone()["next_version"]

            cursor.execute(
                """
                insert into recipe_versions (recipe_id, version_number)
                values (%s, %s)
                returning id, recipe_id, version_number, created_at
                """,
                (recipe_id, next_version),
            )
            version = cursor.fetchone()

        connection.commit()

    return jsonify({"version": serialize_recipe_version_row(version)}), 201
