<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import {
  applyImportDraft,
  createIngredient,
  createIngredientNote,
  createInstruction,
  createRecipeVersion,
  createStep,
  createStepNote,
  deleteIngredient,
  deleteInstruction,
  deleteRecipe,
  deleteRecipeVersion,
  deleteStep,
  fetchRecipe,
  updateIngredientNote,
  updateStep,
  updateStepNote,
  updateIngredient,
} from "../api";
import RecipeImportReview from "../components/RecipeImportReview.vue";
import RecipeIngredientsSection from "../components/RecipeIngredientsSection.vue";
import RecipeInstructionsSection from "../components/RecipeInstructionsSection.vue";
import RecipeVersionHistorySection from "../components/RecipeVersionHistorySection.vue";
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
const deletingIngredientId = ref("");
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
const ingredientGrouping = ref("");
const instructionTitle = ref("");
const isSavingInstruction = ref(false);
const deletingInstructionId = ref("");
const stepBodies = ref<Record<string, string>>({});
const savingStepInstructionId = ref("");
const editingStepIds = ref<Record<string, boolean>>({});
const stepEditBodies = ref<Record<string, string>>({});
const savingEditedStepId = ref("");
const deletingStepId = ref("");
const isVersionHistoryVisible = ref(false);
const ingredientNoteBodies = ref<Record<string, string>>({});
const stepNoteBodies = ref<Record<string, string>>({});
const showingIngredientNoteForms = ref<Record<string, boolean>>({});
const showingStepNoteForms = ref<Record<string, boolean>>({});
const savingIngredientNoteId = ref("");
const savingStepNoteId = ref("");
const editingIngredientNoteIds = ref<Record<string, boolean>>({});
const editingStepNoteIds = ref<Record<string, boolean>>({});
const ingredientNoteEditBodies = ref<Record<string, string>>({});
const stepNoteEditBodies = ref<Record<string, string>>({});
const savingEditedIngredientNoteId = ref("");
const savingEditedStepNoteId = ref("");
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
      grouping: ingredientGrouping.value.trim(),
    });
    ingredientName.value = "";
    ingredientAmount.value = 1;
    ingredientAmountType.value = amountTypes[0];
    ingredientGrouping.value = "";
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

async function removeIngredient(ingredientId: string) {
  const recipeId = route.params.recipeId;
  if (typeof recipeId !== "string") {
    return;
  }

  deletingIngredientId.value = ingredientId;
  errorMessage.value = "";

  try {
    await deleteIngredient(recipeId, ingredientId);
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to delete ingredient";
  } finally {
    deletingIngredientId.value = "";
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

function beginStepEdit(stepId: string, body: string) {
  editingStepIds.value[stepId] = true;
  stepEditBodies.value[stepId] = body;
}

function cancelStepEdit(stepId: string) {
  editingStepIds.value[stepId] = false;
  delete stepEditBodies.value[stepId];
}

async function saveStep(instructionId: string, stepId: string) {
  const recipeId = route.params.recipeId;
  const body = (stepEditBodies.value[stepId] || "").trim();
  if (typeof recipeId !== "string" || !body) {
    return;
  }

  savingEditedStepId.value = stepId;
  errorMessage.value = "";

  try {
    await updateStep(recipeId, instructionId, stepId, body);
    editingStepIds.value[stepId] = false;
    delete stepEditBodies.value[stepId];
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to save step";
  } finally {
    savingEditedStepId.value = "";
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
    showingIngredientNoteForms.value[ingredientId] = false;
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
    showingStepNoteForms.value[stepId] = false;
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to add step note";
  } finally {
    savingStepNoteId.value = "";
  }
}

function beginIngredientNoteEdit(noteId: string, body: string) {
  editingIngredientNoteIds.value[noteId] = true;
  ingredientNoteEditBodies.value[noteId] = body;
}

function cancelIngredientNoteEdit(noteId: string) {
  editingIngredientNoteIds.value[noteId] = false;
  delete ingredientNoteEditBodies.value[noteId];
}

async function saveIngredientNote(ingredientId: string, noteId: string) {
  const recipeId = route.params.recipeId;
  const body = (ingredientNoteEditBodies.value[noteId] || "").trim();
  if (typeof recipeId !== "string" || !body) {
    return;
  }

  savingEditedIngredientNoteId.value = noteId;
  errorMessage.value = "";

  try {
    await updateIngredientNote(recipeId, ingredientId, noteId, body);
    editingIngredientNoteIds.value[noteId] = false;
    delete ingredientNoteEditBodies.value[noteId];
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to save note";
  } finally {
    savingEditedIngredientNoteId.value = "";
  }
}

function beginStepNoteEdit(noteId: string, body: string) {
  editingStepNoteIds.value[noteId] = true;
  stepNoteEditBodies.value[noteId] = body;
}

function cancelStepNoteEdit(noteId: string) {
  editingStepNoteIds.value[noteId] = false;
  delete stepNoteEditBodies.value[noteId];
}

async function saveStepNote(stepId: string, noteId: string) {
  const recipeId = route.params.recipeId;
  const body = (stepNoteEditBodies.value[noteId] || "").trim();
  if (typeof recipeId !== "string" || !body) {
    return;
  }

  savingEditedStepNoteId.value = noteId;
  errorMessage.value = "";

  try {
    await updateStepNote(recipeId, stepId, noteId, body);
    editingStepNoteIds.value[noteId] = false;
    delete stepNoteEditBodies.value[noteId];
    await loadRecipe();
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Unable to save note";
  } finally {
    savingEditedStepNoteId.value = "";
  }
}

function showIngredientNoteForm(ingredientId: string) {
  showingIngredientNoteForms.value[ingredientId] = true;
}

function hideIngredientNoteForm(ingredientId: string) {
  showingIngredientNoteForms.value[ingredientId] = false;
  ingredientNoteBodies.value[ingredientId] = "";
}

function showStepNoteForm(stepId: string) {
  showingStepNoteForms.value[stepId] = true;
}

function hideStepNoteForm(stepId: string) {
  showingStepNoteForms.value[stepId] = false;
  stepNoteBodies.value[stepId] = "";
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
        <div class="recipe-title-row">
          <h2>{{ recipe.name }}</h2>
          <div class="recipe-title-actions">
            <a
              v-if="recipe.inspiration_url"
              :href="recipe.inspiration_url"
              target="_blank"
              rel="noreferrer"
              aria-label="Open inspiration URL"
              title="Open inspiration URL"
            >
              🔗
            </a>
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
        </div>
      </div>

      <RecipeImportReview
        v-if="importDraft"
        :import-draft="importDraft"
        :amount-types="amountTypes"
        :is-applying-import-draft="isApplyingImportDraft"
        @add-ingredient="addDraftIngredient"
        @remove-ingredient="removeDraftIngredient"
        @add-instruction="addDraftInstruction"
        @remove-instruction="removeDraftInstruction"
        @add-step="addDraftStep"
        @remove-step="removeDraftStep"
        @apply="applyDraft"
        @cancel="importDraft = null"
      />

      <RecipeIngredientsSection
        v-if="activeVersion"
        :active-version="activeVersion"
        :amount-types="amountTypes"
        :ingredient-name="ingredientName"
        :ingredient-amount="ingredientAmount"
        :ingredient-amount-type="ingredientAmountType"
        :ingredient-grouping="ingredientGrouping"
        :is-saving-ingredient="isSavingIngredient"
        :editing-ingredient-ids="editingIngredientIds"
        :ingredient-edit-drafts="ingredientEditDrafts"
        :saving-ingredient-id="savingIngredientId"
        :deleting-ingredient-id="deletingIngredientId"
        :showing-ingredient-note-forms="showingIngredientNoteForms"
        :ingredient-note-bodies="ingredientNoteBodies"
        :saving-ingredient-note-id="savingIngredientNoteId"
        :editing-ingredient-note-ids="editingIngredientNoteIds"
        :ingredient-note-edit-bodies="ingredientNoteEditBodies"
        :saving-edited-ingredient-note-id="savingEditedIngredientNoteId"
        @update:ingredient-name="ingredientName = $event"
        @update:ingredient-amount="ingredientAmount = $event"
        @update:ingredient-amount-type="ingredientAmountType = $event"
        @update:ingredient-grouping="ingredientGrouping = $event"
        @add-ingredient="addIngredient"
        @save-ingredient="saveIngredient"
        @remove-ingredient="removeIngredient"
        @cancel-edit="cancelIngredientEdit"
        @begin-edit="beginIngredientEdit"
        @show-note-form="showIngredientNoteForm"
        @add-note="addIngredientNote"
        @hide-note-form="hideIngredientNoteForm"
        @begin-note-edit="beginIngredientNoteEdit"
        @save-note="saveIngredientNote"
        @cancel-note-edit="cancelIngredientNoteEdit"
      />

      <RecipeInstructionsSection
        v-if="activeVersion"
        :active-version="activeVersion"
        :instruction-title="instructionTitle"
        :is-saving-instruction="isSavingInstruction"
        :deleting-instruction-id="deletingInstructionId"
        :step-bodies="stepBodies"
        :saving-step-instruction-id="savingStepInstructionId"
        :editing-step-ids="editingStepIds"
        :step-edit-bodies="stepEditBodies"
        :saving-edited-step-id="savingEditedStepId"
        :deleting-step-id="deletingStepId"
        :showing-step-note-forms="showingStepNoteForms"
        :step-note-bodies="stepNoteBodies"
        :saving-step-note-id="savingStepNoteId"
        :editing-step-note-ids="editingStepNoteIds"
        :step-note-edit-bodies="stepNoteEditBodies"
        :saving-edited-step-note-id="savingEditedStepNoteId"
        @update:instruction-title="instructionTitle = $event"
        @add-instruction="addInstruction"
        @remove-instruction="removeInstruction"
        @add-step="addStep"
        @begin-step-edit="beginStepEdit"
        @save-step="saveStep"
        @cancel-step-edit="cancelStepEdit"
        @remove-step="removeStep"
        @show-note-form="showStepNoteForm"
        @add-note="addStepNote"
        @hide-note-form="hideStepNoteForm"
        @begin-note-edit="beginStepNoteEdit"
        @save-note="saveStepNote"
        @cancel-note-edit="cancelStepNoteEdit"
      />

      <RecipeVersionHistorySection
        :versions="recipe.versions"
        :is-version-history-visible="isVersionHistoryVisible"
        :is-creating-version="isCreatingVersion"
        :deleting-version-id="deletingVersionId"
        @toggle="isVersionHistoryVisible = !isVersionHistoryVisible"
        @add-version="addVersion"
        @remove-version="removeVersion"
      />
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

.recipe-title-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.recipe-title-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

button {
  font: inherit;
}

.icon-button {
  padding: 4px 8px;
  background: transparent;
  color: #6f5036;
  border: 1px solid #a99987;
  cursor: pointer;
}

.danger-button {
  background: #8c2f1d;
}

.danger-icon-button {
  color: white;
  border-color: #8c2f1d;
}
</style>
