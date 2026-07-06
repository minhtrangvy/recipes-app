<script setup lang="ts">
import { reactive } from "vue";

import type { CreateRecipePayload, RecipeCategory } from "../types";

const categories: RecipeCategory[] = [
  "dessert",
  "main",
  "salad",
  "appetizer",
  "cocktail",
  "mocktail",
];

const emit = defineEmits<{
  submit: [payload: CreateRecipePayload];
}>();

const form = reactive<CreateRecipePayload>({
  name: "",
  category: "dessert",
  inspiration_url: null,
});

function onSubmit() {
  emit("submit", {
    name: form.name.trim(),
    category: form.category,
    inspiration_url: form.inspiration_url?.trim() || null,
  });
}
</script>

<template>
  <form class="form-card" @submit.prevent="onSubmit">
    <label>
      Name
      <input v-model="form.name" required type="text" />
    </label>

    <label>
      Category
      <select v-model="form.category">
        <option v-for="category in categories" :key="category" :value="category">
          {{ category }}
        </option>
      </select>
    </label>

    <label>
      Inspiration URL
      <input v-model="form.inspiration_url" type="url" />
    </label>

    <button type="submit">Save recipe</button>
  </form>
</template>

<style scoped>
.form-card {
  display: grid;
  gap: 16px;
  padding: 24px;
  background: #fffaf3;
  border: 1px solid #d4c5b4;
  border-radius: 12px;
}

label {
  display: grid;
  gap: 8px;
  font-weight: 700;
}

input,
select,
button {
  font: inherit;
}

input,
select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #a99987;
  border-radius: 10px;
  background: white;
}

button {
  width: fit-content;
  padding: 10px 16px;
  border: 0;
  background: #1e1a16;
  color: white;
  cursor: pointer;
}
</style>
