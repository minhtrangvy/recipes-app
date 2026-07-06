<script setup lang="ts">
import { onMounted, ref } from "vue";

import { fetchRecipes } from "../api";
import type { RecipeSummary } from "../types";

const recipes = ref<RecipeSummary[]>([]);
const errorMessage = ref("");
const isLoading = ref(true);

onMounted(async () => {
  try {
    recipes.value = await fetchRecipes();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to load recipes";
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <section>
    <p v-if="isLoading">Loading recipes...</p>
    <p v-else-if="errorMessage">{{ errorMessage }}</p>
    <p v-else-if="recipes.length === 0">No recipes yet.</p>

    <div v-else class="recipe-grid">
      <RouterLink
        v-for="recipe in recipes"
        :key="recipe.id"
        :to="`/recipes/${recipe.id}`"
        class="recipe-card"
      >
        <p class="recipe-category">{{ recipe.category }}</p>
        <div class="recipe-title-row">
          <h2>{{ recipe.name }}</h2>
          <span class="version-tag">V{{ recipe.current_version }}</span>
        </div>
        <p v-if="recipe.inspiration_url">{{ recipe.inspiration_url }}</p>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.recipe-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.recipe-card {
  display: block;
  padding: 20px;
  background: #fffaf3;
  border: 1px solid #d4c5b4;
  border-radius: 12px;
  text-decoration: none;
}

.recipe-card h2,
.recipe-card p {
  margin: 0 0 8px;
}

.recipe-title-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: start;
  margin-bottom: 8px;
}

.version-tag {
  flex-shrink: 0;
  padding: 4px 8px;
  border: 1px solid #a99987;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.recipe-category {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 12px;
}
</style>
