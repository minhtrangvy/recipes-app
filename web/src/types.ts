export type RecipeCategory =
  | "dessert"
  | "main"
  | "salad"
  | "appetizer"
  | "cocktail"
  | "mocktail";

export type IngredientAmountType =
  | "cup"
  | "teaspoon"
  | "tablespoon"
  | "dash"
  | "count"
  | "pounds"
  | "to taste"
  | "weight_g";

export interface RecipeSummary {
  id: string;
  name: string;
  category: RecipeCategory;
  inspiration_url: string | null;
  created_at: string;
  current_version: number;
}

export interface RecipeVersion {
  id: string;
  recipe_id: string;
  version_number: number;
  created_at: string;
  ingredient_count: number;
  ingredients: Ingredient[];
  instructions: Instruction[];
}

export interface RecipeVersionSummary {
  id: string;
  recipe_id: string;
  version_number: number;
  created_at: string;
}

export interface Ingredient {
  id: string;
  recipe_version_id: string;
  name: string;
  amount: number;
  amount_type: IngredientAmountType;
  created_at: string;
}

export interface Instruction {
  id: string;
  recipe_version_id: string;
  title: string;
  created_at: string;
  steps: Step[];
}

export interface Step {
  id: string;
  instruction_id: string;
  step_number: number;
  body: string;
  created_at: string;
}

export interface ImportedIngredientDraft {
  name: string;
  amount: number;
  amount_type: IngredientAmountType;
}

export interface ImportedInstructionDraft {
  title: string;
  steps: string[];
}

export interface RecipeImportDraft {
  ingredients: ImportedIngredientDraft[];
  instructions: ImportedInstructionDraft[];
}

export interface RecipeDetail {
  id: string;
  name: string;
  category: RecipeCategory;
  inspiration_url: string | null;
  created_at: string;
  versions: RecipeVersion[];
}

export interface CreateRecipePayload {
  name: string;
  category: RecipeCategory;
  inspiration_url: string | null;
}
