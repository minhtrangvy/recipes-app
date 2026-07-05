import type {
  CreateRecipePayload,
  RecipeDetail,
  RecipeSummary,
  RecipeVersion,
} from "./types";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { error?: string }
      | null;
    throw new Error(body?.error || "Request failed");
  }

  return response.json() as Promise<T>;
}

export async function fetchRecipes(): Promise<RecipeSummary[]> {
  const response = await fetch("/api/recipes");
  const data = await parseResponse<{ recipes: RecipeSummary[] }>(response);
  return data.recipes;
}

export async function fetchRecipe(recipeId: string): Promise<RecipeDetail> {
  const response = await fetch(`/api/recipes/${recipeId}`);
  const data = await parseResponse<{ recipe: RecipeDetail }>(response);
  return data.recipe;
}

export async function createRecipe(
  payload: CreateRecipePayload
): Promise<{ recipe: RecipeSummary; version: RecipeVersion }> {
  const response = await fetch("/api/recipes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseResponse<{ recipe: RecipeSummary; version: RecipeVersion }>(
    response
  );
}

export async function createRecipeVersion(
  recipeId: string
): Promise<RecipeVersion> {
  const response = await fetch(`/api/recipes/${recipeId}/versions`, {
    method: "POST",
  });
  const data = await parseResponse<{ version: RecipeVersion }>(response);
  return data.version;
}
