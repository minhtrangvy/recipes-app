export type RecipeCategory =
  | "dessert"
  | "main"
  | "salad"
  | "appetizer"
  | "cocktail"
  | "mocktail";

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
