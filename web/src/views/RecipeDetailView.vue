<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";

import {
  applyImportDraft,
  fetchImportPreview,
  deleteRecipe,
  deleteStep,
  createIngredient,
  createInstruction,
  createRecipeVersion,
  createStep,
  deleteRecipeVersion,
  fetchRecipe,
} from "../api";
import type {
  ImportedIngredientDraft,
  ImportedInstructionDraft,
  IngredientAmountType,
  RecipeDetail,
  RecipeImportDraft,
} from "../types";

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
const deletingStepId = ref("");
const isLoadingImportPreview = ref(false);
const isApplyingImportDraft = ref(false);
const importDraft = ref<RecipeImportDraft | null>(null);

const amountTypes: IngredientAmountType[] = [
  "cup",
  "teaspoon",
  "tablespoon",
  "dash",
  "count",
  "pounds",
  "to taste",
  "weight_g",
];

const activeVersion = computed(() => recipe.value?.versions[0] ?? null);

function amountTypeLabel(amountType: IngredientAmountType) {
  if (amountType === "weight_g") {
    return "grams";
  }

  return amountType;
}

function formatAmount(amount: number) {
  const fractionMap: Record<string, string> = {
    "0.25": "1/4",
    "0.33": "1/3",
    "0.5": "1/2",
    "0.67": "2/3",
    "0.75": "3/4",
  };

  const rounded = amount.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
  return fractionMap[rounded] || rounded;
}

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

async function removeStep(instructionId: string, stepId: string) {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    return;
  }

  deletingStepId.value = stepId;
  errorMessage.value = "";

  try {
    await deleteStep(recipeId, instructionId, stepId);
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to delete step";
  } finally {
    deletingStepId.value = "";
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

async function loadImportPreview() {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    return;
  }

  isLoadingImportPreview.value = true;
  errorMessage.value = "";

  try {
    const response = await fetchImportPreview(recipeId);
    importDraft.value = response.draft;
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to preview import";
  } finally {
    isLoadingImportPreview.value = false;
  }
}

function addDraftIngredient() {
  if (!importDraft.value) {
    return;
  }

  importDraft.value.ingredients.push({
    name: "",
    amount: 1,
    amount_type: "dash",
  });
}

function removeDraftIngredient(index: number) {
  importDraft.value?.ingredients.splice(index, 1);
}

function addDraftInstruction() {
  if (!importDraft.value) {
    return;
  }

  importDraft.value.instructions.push({
    title: "",
    steps: [""],
  });
}

function removeDraftInstruction(index: number) {
  importDraft.value?.instructions.splice(index, 1);
}

function addDraftStep(instruction: ImportedInstructionDraft) {
  instruction.steps.push("");
}

function removeDraftStep(instruction: ImportedInstructionDraft, index: number) {
  instruction.steps.splice(index, 1);
}

function normalizeDraft(draft: RecipeImportDraft): RecipeImportDraft {
  const ingredients: ImportedIngredientDraft[] = draft.ingredients
    .map((ingredient) => ({
      name: ingredient.name.trim(),
      amount: ingredient.amount,
      amount_type: ingredient.amount_type,
    }))
    .filter((ingredient) => ingredient.name);

  const instructions: ImportedInstructionDraft[] = draft.instructions
    .map((instruction) => ({
      title: instruction.title.trim(),
      steps: instruction.steps.map((step) => step.trim()).filter(Boolean),
    }))
    .filter((instruction) => instruction.title || instruction.steps.length > 0)
    .map((instruction) => ({
      title: instruction.title || "Instruction",
      steps: instruction.steps,
    }));

  return {
    ingredients,
    instructions,
  };
}

async function applyDraft() {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string" || !importDraft.value) {
    return;
  }

  isApplyingImportDraft.value = true;
  errorMessage.value = "";

  try {
    await applyImportDraft(recipeId, normalizeDraft(importDraft.value));
    importDraft.value = null;
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to save imported data";
  } finally {
    isApplyingImportDraft.value = false;
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
        <button
          v-if="recipe.inspiration_url"
          type="button"
          :disabled="isLoadingImportPreview"
          @click="loadImportPreview"
        >
          {{ isLoadingImportPreview ? "Importing..." : "Preview import from URL" }}
        </button>
      </div>

      <div v-if="importDraft" class="versions-card">
        <div class="versions-header">
          <h3>Import review</h3>
          <button type="button" @click="addDraftIngredient">Add ingredient</button>
        </div>

        <div
          v-for="(ingredient, ingredientIndex) in importDraft.ingredients"
          :key="`ingredient-${ingredientIndex}`"
          class="draft-row"
        >
          <input v-model="ingredient.name" type="text" placeholder="Ingredient name" />
          <input
            v-model.number="ingredient.amount"
            min="0.01"
            step="0.01"
            type="number"
          />
          <select v-model="ingredient.amount_type">
            <option
              v-for="amountType in amountTypes"
              :key="`draft-amount-${amountType}`"
              :value="amountType"
            >
              {{ amountTypeLabel(amountType) }}
            </option>
          </select>
          <button
            type="button"
            class="danger-button"
            @click="removeDraftIngredient(ingredientIndex)"
          >
            Remove
          </button>
        </div>

        <div class="versions-header">
          <h3>Instructions</h3>
          <button type="button" @click="addDraftInstruction">Add instruction</button>
        </div>

        <div
          v-for="(instruction, instructionIndex) in importDraft.instructions"
          :key="`instruction-${instructionIndex}`"
          class="instruction-card"
        >
          <div class="draft-row">
            <input
              v-model="instruction.title"
              type="text"
              placeholder="Instruction title"
            />
            <button
              type="button"
              class="danger-button"
              @click="removeDraftInstruction(instructionIndex)"
            >
              Remove
            </button>
          </div>

          <div
            v-for="(step, stepIndex) in instruction.steps"
            :key="`step-${instructionIndex}-${stepIndex}`"
            class="draft-row"
          >
            <input v-model="instruction.steps[stepIndex]" type="text" placeholder="Step" />
            <button
              type="button"
              class="danger-button"
              @click="removeDraftStep(instruction, stepIndex)"
            >
              Remove step
            </button>
          </div>

          <button type="button" @click="addDraftStep(instruction)">Add step</button>
        </div>

        <div class="draft-actions">
          <button type="button" :disabled="isApplyingImportDraft" @click="applyDraft">
            {{ isApplyingImportDraft ? "Saving..." : "Save imported data" }}
          </button>
          <button type="button" class="danger-button" @click="importDraft = null">
            Cancel
          </button>
        </div>
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
            min="0.01"
            step="0.01"
            type="number"
            placeholder="Amount"
          />
          <select v-model="ingredientAmountType">
            <option
              v-for="amountType in amountTypes"
              :key="amountType"
              :value="amountType"
            >
              {{ amountTypeLabel(amountType) }}
            </option>
          </select>
          <button type="submit">
            {{ isSavingIngredient ? "Saving..." : "Add ingredient" }}
          </button>
        </form>

        <p v-if="activeVersion.ingredients.length === 0">No ingredients yet.</p>
        <ul v-else>
          <li v-for="ingredient in activeVersion.ingredients" :key="ingredient.id">
            {{ formatAmount(ingredient.amount) }}
            {{ amountTypeLabel(ingredient.amount_type) }}
            {{ ingredient.name }}
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
              <div class="step-row">
                <span>{{ step.body }}</span>
                <button
                  type="button"
                  class="danger-button"
                  :disabled="deletingStepId !== ''"
                  @click="removeStep(instruction.id, step.id)"
                >
                  {{ deletingStepId === step.id ? "Deleting..." : "Delete step" }}
                </button>
              </div>
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

.draft-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.draft-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.step-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

ul {
  padding-left: 20px;
}
</style>
