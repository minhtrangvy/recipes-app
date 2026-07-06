from flask import Flask, jsonify, request

from api.constants import AMOUNT_TYPES, CATEGORIES
from api.queries import recipes as recipe_queries
from api.services.inspiration_import import import_recipe_from_url

app = Flask(__name__)


def parse_positive_amount(value):
    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)) and value > 0:
        return value

    return None


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


@app.post("/api/recipes/<recipe_id>/import-preview")
def import_preview(recipe_id):
    recipe = recipe_queries.get_recipe(recipe_id)
    if recipe is None:
        return {"error": "recipe not found"}, 404

    if not recipe["inspiration_url"]:
        return {"error": "recipe does not have an inspiration_url"}, 400

    import_payload = import_recipe_from_url(recipe["inspiration_url"])
    active_version = recipe_queries.get_active_version(recipe_id)
    if active_version is None:
        return {"error": "recipe not found"}, 404

    return jsonify(
        {
            "draft": import_payload,
            "active_version": active_version,
        }
    )


@app.post("/api/recipes/<recipe_id>/import-apply")
def import_apply(recipe_id):
    payload = request.get_json(silent=True) or {}
    draft = payload.get("draft")

    if not isinstance(draft, dict):
        return {"error": "draft is required"}, 400

    active_version = recipe_queries.get_active_version(recipe_id)
    if active_version is None:
        return {"error": "recipe not found"}, 404

    recipe_queries.populate_recipe_version_from_import(active_version["id"], draft)
    return "", 204


@app.post("/api/recipes/<recipe_id>/instructions")
def create_instruction(recipe_id):
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()

    result, error = recipe_queries.create_instruction(recipe_id, title)
    if error is not None:
        return {"error": error}, 404

    return jsonify(result), 201


@app.delete("/api/recipes/<recipe_id>/instructions/<instruction_id>")
def delete_instruction(recipe_id, instruction_id):
    error = recipe_queries.delete_instruction(recipe_id, instruction_id)
    if error is not None:
        return {"error": error}, 404

    return "", 204


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


@app.patch("/api/recipes/<recipe_id>/instructions/<instruction_id>/steps/<step_id>")
def update_step(recipe_id, instruction_id, step_id):
    payload = request.get_json(silent=True) or {}
    body = (payload.get("body") or "").strip()
    if not body:
        return {"error": "body is required"}, 400

    result, error = recipe_queries.update_step(recipe_id, instruction_id, step_id, body)
    if error is not None:
        return {"error": error}, 404

    return jsonify(result)


@app.delete("/api/recipes/<recipe_id>/instructions/<instruction_id>/steps/<step_id>")
def delete_step(recipe_id, instruction_id, step_id):
    error = recipe_queries.delete_step(recipe_id, instruction_id, step_id)
    if error is not None:
        return {"error": error}, 404

    return "", 204


@app.post("/api/recipes/<recipe_id>/steps/<step_id>/notes")
def create_step_note(recipe_id, step_id):
    payload = request.get_json(silent=True) or {}
    body = (payload.get("body") or "").strip()
    if not body:
        return {"error": "body is required"}, 400

    result, error = recipe_queries.create_step_note(recipe_id, step_id, body)
    if error is not None:
        return {"error": error}, 404

    return jsonify(result), 201


@app.patch("/api/recipes/<recipe_id>/steps/<step_id>/notes/<note_id>")
def update_step_note(recipe_id, step_id, note_id):
    payload = request.get_json(silent=True) or {}
    body = (payload.get("body") or "").strip()
    if not body:
        return {"error": "body is required"}, 400

    result, error = recipe_queries.update_step_note(recipe_id, step_id, note_id, body)
    if error is not None:
        return {"error": error}, 404

    return jsonify(result)


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
    amount = parse_positive_amount(payload.get("amount"))
    amount_type = payload.get("amount_type")
    grouping = (payload.get("grouping") or "").strip() or None

    if not name:
        return {"error": "name is required"}, 400

    if amount is None:
        return {"error": "amount must be a positive number"}, 400

    if amount_type not in AMOUNT_TYPES:
        return {"error": "amount_type is invalid"}, 400

    result, error = recipe_queries.create_ingredient(
        recipe_id,
        name,
        amount,
        amount_type,
        grouping,
    )
    if error is not None:
        return {"error": error}, 404

    return jsonify(result), 201


@app.patch("/api/recipes/<recipe_id>/ingredients/<ingredient_id>")
def update_ingredient(recipe_id, ingredient_id):
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    amount = parse_positive_amount(payload.get("amount"))
    amount_type = payload.get("amount_type")
    grouping = (payload.get("grouping") or "").strip() or None

    if not name:
        return {"error": "name is required"}, 400

    if amount is None:
        return {"error": "amount must be a positive number"}, 400

    if amount_type not in AMOUNT_TYPES:
        return {"error": "amount_type is invalid"}, 400

    result, error = recipe_queries.update_ingredient(
        recipe_id,
        ingredient_id,
        name,
        amount,
        amount_type,
        grouping,
    )
    if error is not None:
        return {"error": error}, 404

    return jsonify(result)


@app.delete("/api/recipes/<recipe_id>/ingredients/<ingredient_id>")
def delete_ingredient(recipe_id, ingredient_id):
    error = recipe_queries.delete_ingredient(recipe_id, ingredient_id)
    if error is not None:
        return {"error": error}, 404

    return "", 204


@app.post("/api/recipes/<recipe_id>/ingredients/<ingredient_id>/notes")
def create_ingredient_note(recipe_id, ingredient_id):
    payload = request.get_json(silent=True) or {}
    body = (payload.get("body") or "").strip()
    if not body:
        return {"error": "body is required"}, 400

    result, error = recipe_queries.create_ingredient_note(recipe_id, ingredient_id, body)
    if error is not None:
        return {"error": error}, 404

    return jsonify(result), 201


@app.patch("/api/recipes/<recipe_id>/ingredients/<ingredient_id>/notes/<note_id>")
def update_ingredient_note(recipe_id, ingredient_id, note_id):
    payload = request.get_json(silent=True) or {}
    body = (payload.get("body") or "").strip()
    if not body:
        return {"error": "body is required"}, 400

    result, error = recipe_queries.update_ingredient_note(
        recipe_id, ingredient_id, note_id, body
    )
    if error is not None:
        return {"error": error}, 404

    return jsonify(result)


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
