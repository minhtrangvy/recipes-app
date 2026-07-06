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
