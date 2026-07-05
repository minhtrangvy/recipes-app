<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { createRecipeVersion, fetchRecipe } from "../api";
import type { RecipeDetail } from "../types";

const route = useRoute();
const recipe = ref<RecipeDetail | null>(null);
const errorMessage = ref("");
const isLoading = ref(true);
const isCreatingVersion = ref(false);

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
            Version {{ version.version_number }} ·
            {{ version.ingredient_count }} ingredients
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

button {
  font: inherit;
  padding: 10px 16px;
  border: 0;
  background: #1e1a16;
  color: white;
  cursor: pointer;
}

ul {
  padding-left: 20px;
}
</style>
