import type {
  CreateRecipePayload,
  Ingredient,
  IngredientAmountType,
  ImportedInstructionDraft,
  RecipeImportDraft,
  Instruction,
  RecipeDetail,
  RecipeSummary,
  RecipeVersion,
  RecipeVersionSummary,
  Step,
} from "./types";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { error?: string }
      | null;
    throw new Error(body?.error || "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
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
): Promise<{ recipe: RecipeSummary; version: RecipeVersionSummary }> {
  const response = await fetch("/api/recipes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseResponse<{ recipe: RecipeSummary; version: RecipeVersionSummary }>(
    response
  );
}

export async function fetchImportPreview(
  recipeId: string
): Promise<{ draft: RecipeImportDraft; active_version: RecipeVersionSummary }> {
  const response = await fetch(`/api/recipes/${recipeId}/import-preview`, {
    method: "POST",
  });
  return parseResponse<{
    draft: RecipeImportDraft;
    active_version: RecipeVersionSummary;
  }>(response);
}

export async function applyImportDraft(
  recipeId: string,
  draft: RecipeImportDraft
): Promise<void> {
  const normalizedInstructions: ImportedInstructionDraft[] = draft.instructions.map(
    (instruction) => ({
      title: instruction.title,
      steps: instruction.steps,
    })
  );

  const response = await fetch(`/api/recipes/${recipeId}/import-apply`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      draft: {
        ingredients: draft.ingredients,
        instructions: normalizedInstructions,
      },
    }),
  });
  await parseResponse(response);
}

export async function createRecipeVersion(
  recipeId: string
): Promise<RecipeVersionSummary> {
  const response = await fetch(`/api/recipes/${recipeId}/versions`, {
    method: "POST",
  });
  const data = await parseResponse<{ version: RecipeVersionSummary }>(response);
  return data.version;
}

export async function createIngredient(
  recipeId: string,
  payload: {
    name: string;
    amount: number;
    amount_type: IngredientAmountType;
    grouping?: string;
  }
): Promise<{ ingredient: Ingredient; active_version: RecipeVersionSummary }> {
  const response = await fetch(`/api/recipes/${recipeId}/ingredients`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return parseResponse<{
    ingredient: Ingredient;
    active_version: RecipeVersionSummary;
  }>(response);
}

export async function updateIngredient(
  recipeId: string,
  ingredientId: string,
  payload: {
    name: string;
    amount: number;
    amount_type: IngredientAmountType;
    grouping?: string;
  }
): Promise<{ ingredient: Ingredient }> {
  const response = await fetch(`/api/recipes/${recipeId}/ingredients/${ingredientId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return parseResponse<{ ingredient: Ingredient }>(response);
}

export async function deleteRecipeVersion(
  recipeId: string,
  versionId: string
): Promise<void> {
  const response = await fetch(`/api/recipes/${recipeId}/versions/${versionId}`, {
    method: "DELETE",
  });
  await parseResponse(response);
}

export async function deleteRecipe(recipeId: string): Promise<void> {
  const response = await fetch(`/api/recipes/${recipeId}`, {
    method: "DELETE",
  });
  await parseResponse(response);
}

export async function createInstruction(
  recipeId: string,
  title: string
): Promise<{ instruction: Instruction; active_version: RecipeVersionSummary }> {
  const response = await fetch(`/api/recipes/${recipeId}/instructions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title }),
  });
  return parseResponse<{
    instruction: Instruction;
    active_version: RecipeVersionSummary;
  }>(response);
}

export async function deleteInstruction(
  recipeId: string,
  instructionId: string
): Promise<void> {
  const response = await fetch(`/api/recipes/${recipeId}/instructions/${instructionId}`, {
    method: "DELETE",
  });
  await parseResponse(response);
}

export async function createStep(
  recipeId: string,
  instructionId: string,
  body: string
): Promise<{ step: Step }> {
  const response = await fetch(
    `/api/recipes/${recipeId}/instructions/${instructionId}/steps`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ body }),
    }
  );
  return parseResponse<{ step: Step }>(response);
}

export async function deleteStep(
  recipeId: string,
  instructionId: string,
  stepId: string
): Promise<void> {
  const response = await fetch(
    `/api/recipes/${recipeId}/instructions/${instructionId}/steps/${stepId}`,
    {
      method: "DELETE",
    }
  );
  await parseResponse(response);
}
