<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";

import {
  applyImportDraft,
  createIngredientNote,
  createStepNote,
  fetchImportPreview,
  deleteRecipe,
  deleteInstruction,
  deleteStep,
  createIngredient,
  createInstruction,
  createRecipeVersion,
  createStep,
  deleteRecipeVersion,
  fetchRecipe,
  updateIngredient,
} from "../api";
import type {
  Ingredient,
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
const savingIngredientId = ref("");
const editingIngredientIds = ref<Record<string, boolean>>({});
const ingredientEditDrafts = ref<
  Record<
    string,
    {
      name: string;
      amount: number;
      amount_type: IngredientAmountType;
      grouping: string;
    }
  >
>({});
const deletingVersionId = ref("");
const isDeletingRecipe = ref(false);
const ingredientName = ref("");
const ingredientAmount = ref(1);
const instructionTitle = ref("");
const isSavingInstruction = ref(false);
const deletingInstructionId = ref("");
const stepBodies = ref<Record<string, string>>({});
const savingStepInstructionId = ref("");
const deletingStepId = ref("");
const ingredientNoteBodies = ref<Record<string, string>>({});
const stepNoteBodies = ref<Record<string, string>>({});
const savingIngredientNoteId = ref("");
const savingStepNoteId = ref("");
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

const ingredientAmountType = ref<IngredientAmountType>(amountTypes[0]);

const activeVersion = computed(() => recipe.value?.versions[0] ?? null);

const groupedActiveIngredients = computed(() => {
  const ingredients = activeVersion.value?.ingredients ?? [];
  const groups = new Map<string, Ingredient[]>();

  for (const ingredient of ingredients) {
    const groupName = ingredient.grouping || "";
    if (!groups.has(groupName)) {
      groups.set(groupName, []);
    }
    groups.get(groupName)!.push(ingredient);
  }

  return Array.from(groups.entries()).map(([grouping, ingredientsInGroup]) => ({
    grouping,
    ingredients: ingredientsInGroup,
  }));
});

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
      grouping: "",
    });
    ingredientName.value = "";
    ingredientAmount.value = 1;
    ingredientAmountType.value = amountTypes[0];
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to add ingredient";
  } finally {
    isSavingIngredient.value = false;
  }
}

async function saveIngredient(ingredient: Ingredient) {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    return;
  }

  const draft = ingredientEditDrafts.value[ingredient.id];
  if (!draft) {
    return;
  }

  savingIngredientId.value = ingredient.id;
  errorMessage.value = "";

  try {
    await updateIngredient(recipeId, ingredient.id, {
      name: draft.name.trim(),
      amount: draft.amount,
      amount_type: draft.amount_type,
      grouping: draft.grouping.trim(),
    });
    editingIngredientIds.value[ingredient.id] = false;
    delete ingredientEditDrafts.value[ingredient.id];
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to save ingredient";
  } finally {
    savingIngredientId.value = "";
  }
}

function beginIngredientEdit(ingredient: Ingredient) {
  editingIngredientIds.value[ingredient.id] = true;
  ingredientEditDrafts.value[ingredient.id] = {
    name: ingredient.name,
    amount: ingredient.amount,
    amount_type: ingredient.amount_type,
    grouping: ingredient.grouping,
  };
}

function cancelIngredientEdit(ingredientId: string) {
  editingIngredientIds.value[ingredientId] = false;
  delete ingredientEditDrafts.value[ingredientId];
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
  if (typeof recipeId !== "string") {
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

async function removeInstruction(instructionId: string) {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    return;
  }

  deletingInstructionId.value = instructionId;
  errorMessage.value = "";

  try {
    await deleteInstruction(recipeId, instructionId);
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to delete instruction";
  } finally {
    deletingInstructionId.value = "";
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

async function addIngredientNote(ingredientId: string) {
  const recipeId = route.params.recipeId;
  const body = (ingredientNoteBodies.value[ingredientId] || "").trim();
  if (typeof recipeId !== "string" || !body) {
    return;
  }

  savingIngredientNoteId.value = ingredientId;
  errorMessage.value = "";

  try {
    await createIngredientNote(recipeId, ingredientId, body);
    ingredientNoteBodies.value[ingredientId] = "";
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to add ingredient note";
  } finally {
    savingIngredientNoteId.value = "";
  }
}

async function addStepNote(stepId: string) {
  const recipeId = route.params.recipeId;
  const body = (stepNoteBodies.value[stepId] || "").trim();
  if (typeof recipeId !== "string" || !body) {
    return;
  }

  savingStepNoteId.value = stepId;
  errorMessage.value = "";

  try {
    await createStepNote(recipeId, stepId, body);
    stepNoteBodies.value[stepId] = "";
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to add step note";
  } finally {
    savingStepNoteId.value = "";
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
          class="danger-button icon-button danger-icon-button"
          :disabled="isDeletingRecipe"
          :aria-label="isDeletingRecipe ? 'Deleting recipe' : 'Delete recipe'"
          @click="removeRecipe"
        >
          {{ isDeletingRecipe ? "Deleting..." : "🗑️" }}
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
          <p>V{{ activeVersion.version_number }}</p>
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
          <button type="submit" :aria-label="isSavingIngredient ? 'Saving ingredient' : 'Add ingredient'">
            {{ isSavingIngredient ? "Saving..." : "➕" }}
          </button>
        </form>

        <p v-if="activeVersion.ingredients.length === 0">No ingredients yet.</p>
        <div v-else>
          <div
            v-for="group in groupedActiveIngredients"
            :key="group.grouping || 'ungrouped'"
            class="ingredient-group"
          >
            <h4 v-if="group.grouping">{{ group.grouping }}</h4>
            <ul>
              <li v-for="ingredient in group.ingredients" :key="ingredient.id">
                <div v-if="editingIngredientIds[ingredient.id]" class="ingredient-edit-row">
                  <input
                    v-model="ingredientEditDrafts[ingredient.id].name"
                    type="text"
                    placeholder="Ingredient name"
                  />
                  <input
                    v-model.number="ingredientEditDrafts[ingredient.id].amount"
                    min="0.01"
                    step="0.01"
                    type="number"
                  />
                  <select v-model="ingredientEditDrafts[ingredient.id].amount_type">
                    <option
                      v-for="amountType in amountTypes"
                      :key="`existing-${ingredient.id}-${amountType}`"
                      :value="amountType"
                    >
                      {{ amountTypeLabel(amountType) }}
                    </option>
                  </select>
                  <input
                    v-model="ingredientEditDrafts[ingredient.id].grouping"
                    type="text"
                    placeholder="Grouping"
                  />
                  <button
                    type="button"
                    :disabled="savingIngredientId !== ''"
                    @click="saveIngredient(ingredient)"
                  >
                    {{ savingIngredientId === ingredient.id ? "Saving..." : "Save" }}
                  </button>
                  <button type="button" @click="cancelIngredientEdit(ingredient.id)">
                    Cancel
                  </button>
                </div>
                <div v-else class="ingredient-display-row">
                  <div class="item-with-note">
                    <div class="item-main">
                      <p class="ingredient-preview">
                        {{ formatAmount(ingredient.amount) }}
                        {{ amountTypeLabel(ingredient.amount_type) }}
                        {{ ingredient.name }}
                      </p>
                      <button
                        type="button"
                        class="icon-button"
                        aria-label="Edit ingredient"
                        @click="beginIngredientEdit(ingredient)"
                      >
                        ✎
                      </button>
                    </div>
                    <div v-if="ingredient.notes.length > 0" class="note-stack">
                      <div
                        v-for="note in ingredient.notes"
                        :key="note.id"
                        class="note-callout"
                      >
                        Important note: {{ note.body }}
                      </div>
                    </div>
                    <form class="note-form" @submit.prevent="addIngredientNote(ingredient.id)">
                      <input
                        v-model="ingredientNoteBodies[ingredient.id]"
                        type="text"
                        placeholder="Add note for next time"
                      />
                      <button type="submit">
                        {{
                          savingIngredientNoteId === ingredient.id
                            ? "Saving..."
                            : "Add note"
                        }}
                      </button>
                    </form>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="activeVersion" class="versions-card">
        <div class="versions-header">
          <h3>Instructions</h3>
        </div>

        <form class="instruction-form" @submit.prevent="addInstruction">
          <input
            v-model="instructionTitle"
            type="text"
            placeholder="Instruction title (optional)"
          />
          <button
            type="submit"
            :aria-label="isSavingInstruction ? 'Saving instruction' : 'Add instruction'"
          >
            {{ isSavingInstruction ? "Saving..." : "➕📄" }}
          </button>
        </form>

        <p v-if="activeVersion.instructions.length === 0">No instructions yet.</p>
        <div
          v-else
          v-for="instruction in activeVersion.instructions"
          :key="instruction.id"
          class="instruction-card"
        >
          <div class="instruction-header">
            <h4 v-if="instruction.title">{{ instruction.title }}</h4>
            <button
              type="button"
              class="danger-button"
              :disabled="deletingInstructionId !== ''"
              :aria-label="
                deletingInstructionId === instruction.id
                  ? 'Deleting instruction'
                  : 'Delete instruction'
              "
              @click="removeInstruction(instruction.id)"
            >
              {{ deletingInstructionId === instruction.id ? "Deleting..." : "🗑️📄" }}
            </button>
          </div>
          <ol v-if="instruction.steps.length > 0">
            <li v-for="step in instruction.steps" :key="step.id">
              <div class="item-with-note">
                <div class="step-row">
                  <span>{{ step.body }}</span>
                  <button
                    type="button"
                    class="danger-button"
                    :disabled="deletingStepId !== ''"
                    :aria-label="
                      deletingStepId === step.id ? 'Deleting step' : 'Delete step'
                    "
                    @click="removeStep(instruction.id, step.id)"
                  >
                    {{ deletingStepId === step.id ? "Deleting..." : "🗑️" }}
                  </button>
                </div>
                <div v-if="step.notes.length > 0" class="note-stack">
                  <div v-for="note in step.notes" :key="note.id" class="note-callout">
                    Important note: {{ note.body }}
                  </div>
                </div>
                <form class="note-form" @submit.prevent="addStepNote(step.id)">
                  <input
                    v-model="stepNoteBodies[step.id]"
                    type="text"
                    placeholder="Add note for next time"
                  />
                  <button type="submit">
                    {{ savingStepNoteId === step.id ? "Saving..." : "Add note" }}
                  </button>
                </form>
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
            <button
              type="submit"
              :aria-label="
                savingStepInstructionId === instruction.id ? 'Saving step' : 'Add step'
              "
            >
              {{
                savingStepInstructionId === instruction.id ? "Saving..." : "➕"
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
                V{{ version.version_number }} ·
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

.instruction-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
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

.ingredient-group + .ingredient-group {
  margin-top: 20px;
}

.ingredient-edit-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.ingredient-display-row {
  width: 100%;
}

.ingredient-preview {
  margin: 8px 0 0;
}

.icon-button {
  padding: 4px 8px;
  background: transparent;
  color: #1e1a16;
  border: 1px solid #a99987;
}

.danger-icon-button {
  color: white;
  border-color: #8c2f1d;
}

.item-with-note {
  display: grid;
  gap: 10px;
}

.item-main {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.note-stack {
  display: grid;
  gap: 8px;
}

.note-callout {
  padding: 10px 12px;
  background: #fff1c7;
  border-left: 4px solid #d68b00;
  color: #5b3a00;
  font-weight: 700;
}

.note-form {
  display: flex;
  gap: 12px;
}

ul {
  padding-left: 20px;
}
</style>
