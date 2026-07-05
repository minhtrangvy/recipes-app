<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { createRecipe } from "../api";
import RecipeForm from "../components/RecipeForm.vue";
import type { CreateRecipePayload } from "../types";

const router = useRouter();
const errorMessage = ref("");
const isSaving = ref(false);

async function submitRecipe(payload: CreateRecipePayload) {
  errorMessage.value = "";
  isSaving.value = true;

  try {
    const { recipe } = await createRecipe(payload);
    await router.push(`/recipes/${recipe.id}`);
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to save recipe";
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <section>
    <p>Create a recipe and automatically start version 1.</p>
    <p v-if="errorMessage">{{ errorMessage }}</p>
    <p v-if="isSaving">Saving...</p>
    <RecipeForm @submit="submitRecipe" />
  </section>
</template>
