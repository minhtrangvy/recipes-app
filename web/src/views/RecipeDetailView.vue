<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";

import {
  deleteRecipe,
  createIngredient,
  createInstruction,
  createRecipeVersion,
  createStep,
  deleteRecipeVersion,
  fetchRecipe,
} from "../api";
import type { IngredientAmountType, RecipeDetail } from "../types";

const route = useRoute();
const router = useRouter();
const recipe = ref<RecipeDetail | null>(null);
const errorMessage = ref("");
const isLoading = ref(true);
const isCreatingVersion = ref(false);
const isSavingIngredient = ref(false);
const deletingVersionId = ref("");
const isDeletingRecipe = ref(false);
const ingredientName = ref("");
const ingredientAmount = ref(1);
const ingredientAmountType = ref<IngredientAmountType>("dash");
const instructionTitle = ref("");
const isSavingInstruction = ref(false);
const stepBodies = ref<Record<string, string>>({});
const savingStepInstructionId = ref("");

const amountTypes: IngredientAmountType[] = [
  "cup",
  "teaspoon",
  "tablespoon",
  "dash",
  "weight_g",
];

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
  if (typeof recipeId !== "string" || !name || ingredientAmount.value <= 0) {
    return;
  }

  isSavingIngredient.value = true;
  errorMessage.value = "";

  try {
    await createIngredient(recipeId, {
      name,
      amount: ingredientAmount.value,
      amount_type: ingredientAmountType.value,
    });
    ingredientName.value = "";
    ingredientAmount.value = 1;
    ingredientAmountType.value = "dash";
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

async function addInstruction() {
  const recipeId = route.params.recipeId;
  const title = instructionTitle.value.trim();
  if (typeof recipeId !== "string" || !title) {
    return;
  }

  isSavingInstruction.value = true;
  errorMessage.value = "";

  try {
    await createInstruction(recipeId, title);
    instructionTitle.value = "";
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to add instruction";
  } finally {
    isSavingInstruction.value = false;
  }
}

async function addStep(instructionId: string) {
  const recipeId = route.params.recipeId;
  const body = (stepBodies.value[instructionId] || "").trim();
  if (typeof recipeId !== "string" || !body) {
    return;
  }

  savingStepInstructionId.value = instructionId;
  errorMessage.value = "";

  try {
    await createStep(recipeId, instructionId, body);
    stepBodies.value[instructionId] = "";
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to add step";
  } finally {
    savingStepInstructionId.value = "";
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

async function removeRecipe() {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    return;
  }

  isDeletingRecipe.value = true;
  errorMessage.value = "";

  try {
    await deleteRecipe(recipeId);
    await router.push("/");
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to delete recipe";
  } finally {
    isDeletingRecipe.value = false;
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
        <button
          type="button"
          class="danger-button"
          :disabled="isDeletingRecipe"
          @click="removeRecipe"
        >
          {{ isDeletingRecipe ? "Deleting..." : "Delete recipe" }}
        </button>
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
          <input
            v-model.number="ingredientAmount"
            min="1"
            type="number"
            placeholder="Amount"
          />
          <select v-model="ingredientAmountType">
            <option
              v-for="amountType in amountTypes"
              :key="amountType"
              :value="amountType"
            >
              {{ amountType }}
            </option>
          </select>
          <button type="submit">
            {{ isSavingIngredient ? "Saving..." : "Add ingredient" }}
          </button>
        </form>

        <p v-if="activeVersion.ingredients.length === 0">No ingredients yet.</p>
        <ul v-else>
          <li v-for="ingredient in activeVersion.ingredients" :key="ingredient.id">
            {{ ingredient.amount }} {{ ingredient.amount_type }} {{ ingredient.name }}
          </li>
        </ul>
      </div>

      <div v-if="activeVersion" class="versions-card">
        <div class="versions-header">
          <h3>Instructions</h3>
        </div>

        <form class="instruction-form" @submit.prevent="addInstruction">
          <input
            v-model="instructionTitle"
            type="text"
            placeholder="Instruction title"
          />
          <button type="submit">
            {{ isSavingInstruction ? "Saving..." : "Add instruction" }}
          </button>
        </form>

        <p v-if="activeVersion.instructions.length === 0">No instructions yet.</p>
        <div
          v-else
          v-for="instruction in activeVersion.instructions"
          :key="instruction.id"
          class="instruction-card"
        >
          <h4>{{ instruction.title }}</h4>
          <ol v-if="instruction.steps.length > 0">
            <li v-for="step in instruction.steps" :key="step.id">
              {{ step.body }}
            </li>
          </ol>
          <p v-else>No steps yet.</p>

          <form class="instruction-form" @submit.prevent="addStep(instruction.id)">
            <input
              v-model="stepBodies[instruction.id]"
              type="text"
              placeholder="Add step"
            />
            <button type="submit">
              {{
                savingStepInstructionId === instruction.id ? "Saving..." : "Add step"
              }}
            </button>
          </form>
        </div>
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

.instruction-form {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

input,
select,
button {
  font: inherit;
}

input,
select {
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

.instruction-card + .instruction-card {
  margin-top: 20px;
}

ul {
  padding-left: 20px;
}
</style>
