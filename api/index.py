from flask import Flask, jsonify, request

from api.queries import recipes as recipe_queries


CATEGORIES = (
    "dessert",
    "main",
    "salad",
    "appetizer",
    "cocktail",
    "mocktail",
)

AMOUNT_TYPES = (
    "cup",
    "teaspoon",
    "tablespoon",
    "dash",
    "weight_g",
)

app = Flask(__name__)


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
    return jsonify({"recipes": recipe_queries.list_recipes()})


@app.get("/api/recipes/<recipe_id>")
def get_recipe(recipe_id):
    recipe = recipe_queries.get_recipe(recipe_id)
    if recipe is None:
        return {"error": "recipe not found"}, 404

    return jsonify({"recipe": recipe})


@app.post("/api/recipes")
def create_recipe():
    payload, error = validate_recipe_payload(request.get_json(silent=True) or {})
    if error is not None:
        message, status_code = error
        return {"error": message}, status_code

    result = recipe_queries.create_recipe(
        payload["name"],
        payload["category"],
        payload["inspiration_url"],
    )
    return jsonify(result), 201


@app.post("/api/recipes/<recipe_id>/instructions")
def create_instruction(recipe_id):
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return {"error": "title is required"}, 400

    result, error = recipe_queries.create_instruction(recipe_id, title)
    if error is not None:
        return {"error": error}, 404

    return jsonify(result), 201


@app.post("/api/recipes/<recipe_id>/instructions/<instruction_id>/steps")
def create_step(recipe_id, instruction_id):
    payload = request.get_json(silent=True) or {}
    body = (payload.get("body") or "").strip()
    if not body:
        return {"error": "body is required"}, 400

    result, error = recipe_queries.create_step(recipe_id, instruction_id, body)
    if error is not None:
        return {"error": error}, 404

    return jsonify(result), 201


@app.post("/api/recipes/<recipe_id>/versions")
def create_recipe_version(recipe_id):
    version, error = recipe_queries.create_recipe_version(recipe_id)
    if error is not None:
        return {"error": error}, 404

    return jsonify({"version": version}), 201


@app.post("/api/recipes/<recipe_id>/ingredients")
def create_ingredient(recipe_id):
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    amount = payload.get("amount")
    amount_type = payload.get("amount_type")

    if not name:
        return {"error": "name is required"}, 400

    if not isinstance(amount, int) or amount <= 0:
        return {"error": "amount must be a positive integer"}, 400

    if amount_type not in AMOUNT_TYPES:
        return {"error": "amount_type is invalid"}, 400

    result, error = recipe_queries.create_ingredient(
        recipe_id,
        name,
        amount,
        amount_type,
    )
    if error is not None:
        return {"error": error}, 404

    return jsonify(result), 201


@app.delete("/api/recipes/<recipe_id>/versions/<version_id>")
def delete_recipe_version(recipe_id, version_id):
    error = recipe_queries.delete_recipe_version(recipe_id, version_id)
    if error == "version not found":
        return {"error": error}, 404
    if error is not None:
        return {"error": error}, 400

    return "", 204


@app.delete("/api/recipes/<recipe_id>")
def delete_recipe(recipe_id):
    error = recipe_queries.delete_recipe(recipe_id)
    if error is not None:
        return {"error": error}, 404

    return "", 204
