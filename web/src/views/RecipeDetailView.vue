<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import {
  createIngredient,
  createRecipeVersion,
  deleteRecipeVersion,
  fetchRecipe,
} from "../api";
import type { RecipeDetail } from "../types";

const route = useRoute();
const recipe = ref<RecipeDetail | null>(null);
const errorMessage = ref("");
const isLoading = ref(true);
const isCreatingVersion = ref(false);
const isSavingIngredient = ref(false);
const deletingVersionId = ref("");
const ingredientName = ref("");

const activeVersion = computed(() => recipe.value?.versions[0] ?? null);

async function loadRecipe() {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    errorMessage.value = "Invalid recipe id";
    isLoading.value = false;
    return;
  }

  try {
    recipe.value = await fetchRecipe(recipeId);
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to load recipe";
  } finally {
    isLoading.value = false;
  }
}

async function addIngredient() {
  const recipeId = route.params.recipeId;
  const name = ingredientName.value.trim();
  if (typeof recipeId !== "string" || !name) {
    return;
  }

  isSavingIngredient.value = true;
  errorMessage.value = "";

  try {
    await createIngredient(recipeId, name);
    ingredientName.value = "";
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to add ingredient";
  } finally {
    isSavingIngredient.value = false;
  }
}

async function addVersion() {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    return;
  }

  isCreatingVersion.value = true;

  try {
    await createRecipeVersion(recipeId);
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to add version";
  } finally {
    isCreatingVersion.value = false;
  }
}

async function removeVersion(versionId: string) {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    return;
  }

  deletingVersionId.value = versionId;
  errorMessage.value = "";

  try {
    await deleteRecipeVersion(recipeId, versionId);
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to delete version";
  } finally {
    deletingVersionId.value = "";
  }
}

onMounted(loadRecipe);
</script>

<template>
  <section>
    <p v-if="isLoading">Loading recipe...</p>
    <p v-else-if="errorMessage">{{ errorMessage }}</p>

    <div v-else-if="recipe" class="detail-layout">
      <div>
        <p class="recipe-category">{{ recipe.category }}</p>
        <h2>{{ recipe.name }}</h2>
        <p v-if="recipe.inspiration_url">
          <a :href="recipe.inspiration_url" target="_blank" rel="noreferrer">
            {{ recipe.inspiration_url }}
          </a>
        </p>
      </div>

      <div v-if="activeVersion" class="versions-card">
        <div class="versions-header">
          <h3>Active version</h3>
          <p>Version {{ activeVersion.version_number }}</p>
        </div>

        <form class="ingredient-form" @submit.prevent="addIngredient">
          <input
            v-model="ingredientName"
            type="text"
            placeholder="Add ingredient"
          />
          <button type="submit">
            {{ isSavingIngredient ? "Saving..." : "Add ingredient" }}
          </button>
        </form>

        <p v-if="activeVersion.ingredients.length === 0">No ingredients yet.</p>
        <ul v-else>
          <li v-for="ingredient in activeVersion.ingredients" :key="ingredient.id">
            {{ ingredient.name }}
          </li>
        </ul>
      </div>

      <div class="versions-card">
        <div class="versions-header">
          <h3>Versions</h3>
          <button type="button" @click="addVersion">
            {{ isCreatingVersion ? "Adding..." : "Add version" }}
          </button>
        </div>

        <p v-if="recipe.versions.length === 0">No versions yet.</p>

        <ul v-else>
          <li v-for="version in recipe.versions" :key="version.id">
            <div class="version-row">
              <span>
                Version {{ version.version_number }} ·
                {{ version.ingredient_count }} ingredients
              </span>
              <button
                type="button"
                class="danger-button"
                :disabled="recipe.versions.length === 1 || deletingVersionId !== ''"
                @click="removeVersion(version.id)"
              >
                {{
                  deletingVersionId === version.id ? "Deleting..." : "Delete version"
                }}
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
.detail-layout {
  display: grid;
  gap: 24px;
}

.recipe-category {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 12px;
}

.versions-card {
  padding: 24px;
  background: #fffaf3;
  border: 1px solid #d4c5b4;
}

.versions-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.ingredient-form {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

input,
button {
  font: inherit;
}

input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #a99987;
  background: white;
}

button {
  padding: 10px 16px;
  border: 0;
  background: #1e1a16;
  color: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: default;
}

.danger-button {
  background: #8c2f1d;
}

.version-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

ul {
  padding-left: 20px;
}
</style>
