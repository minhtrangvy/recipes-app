<script setup lang="ts">
import { computed } from "vue";

import type { Ingredient, IngredientAmountType, RecipeVersion } from "../types";

interface IngredientEditDraft {
  name: string;
  amount: number;
  amount_type: IngredientAmountType;
  grouping: string;
}

const props = defineProps<{
  activeVersion: RecipeVersion;
  amountTypes: IngredientAmountType[];
  ingredientName: string;
  ingredientAmount: number;
  ingredientAmountType: IngredientAmountType;
  ingredientGrouping: string;
  isSavingIngredient: boolean;
  editingIngredientIds: Record<string, boolean>;
  ingredientEditDrafts: Record<string, IngredientEditDraft>;
  savingIngredientId: string;
  deletingIngredientId: string;
  showingIngredientNoteForms: Record<string, boolean>;
  ingredientNoteBodies: Record<string, string>;
  savingIngredientNoteId: string;
  editingIngredientNoteIds: Record<string, boolean>;
  ingredientNoteEditBodies: Record<string, string>;
  savingEditedIngredientNoteId: string;
  deletingIngredientNoteId: string;
}>();

defineEmits<{
  (event: "update:ingredientName", value: string): void;
  (event: "update:ingredientAmount", value: number): void;
  (event: "update:ingredientAmountType", value: IngredientAmountType): void;
  (event: "update:ingredientGrouping", value: string): void;
  (event: "add-ingredient"): void;
  (event: "save-ingredient", ingredient: Ingredient): void;
  (event: "remove-ingredient", ingredientId: string): void;
  (event: "cancel-edit", ingredientId: string): void;
  (event: "begin-edit", ingredient: Ingredient): void;
  (event: "show-note-form", ingredientId: string): void;
  (event: "add-note", ingredientId: string): void;
  (event: "hide-note-form", ingredientId: string): void;
  (event: "begin-note-edit", noteId: string, body: string): void;
  (event: "save-note", ingredientId: string, noteId: string): void;
  (event: "remove-note", ingredientId: string, noteId: string): void;
  (event: "cancel-note-edit", noteId: string): void;
}>();

const groupedActiveIngredients = computed(() => {
  const groups = new Map<string, Ingredient[]>();

  for (const ingredient of props.activeVersion.ingredients) {
    const groupName = ingredient.grouping || "";
    if (!groups.has(groupName)) {
      groups.set(groupName, []);
    }
    groups.get(groupName)!.push(ingredient);
  }

  return Array.from(groups.entries()).map(([grouping, ingredients]) => ({
    grouping,
    ingredients,
  }));
});

const existingGroupings = computed(() =>
  groupedActiveIngredients.value
    .map((group) => group.grouping)
    .filter((grouping) => grouping),
);

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
</script>

<template>
  <div class="section-card">
    <form class="ingredient-form" @submit.prevent="$emit('add-ingredient')">
      <input
        :value="props.ingredientName"
        type="text"
        placeholder="Add ingredient"
        @input="$emit('update:ingredientName', ($event.target as HTMLInputElement).value)"
      />
      <input
        :value="props.ingredientAmount"
        min="0.01"
        step="0.01"
        type="number"
        placeholder="Amount"
        @input="
          $emit(
            'update:ingredientAmount',
            Number(($event.target as HTMLInputElement).value),
          )
        "
      />
      <select
        :value="props.ingredientAmountType"
        @change="
          $emit(
            'update:ingredientAmountType',
            ($event.target as HTMLSelectElement).value as IngredientAmountType,
          )
        "
      >
        <option v-for="amountType in props.amountTypes" :key="amountType" :value="amountType">
          {{ amountTypeLabel(amountType) }}
        </option>
      </select>
      <input
        :value="props.ingredientGrouping"
        list="ingredient-groupings"
        type="text"
        placeholder="Grouping"
        @input="
          $emit(
            'update:ingredientGrouping',
            ($event.target as HTMLInputElement).value,
          )
        "
      />
      <datalist id="ingredient-groupings">
        <option
          v-for="grouping in existingGroupings"
          :key="`grouping-${grouping}`"
          :value="grouping"
        />
      </datalist>
      <button
        type="submit"
        class="icon-button"
        :aria-label="props.isSavingIngredient ? 'Saving ingredient' : 'Add ingredient'"
      >
        {{ props.isSavingIngredient ? "Saving..." : "➕" }}
      </button>
    </form>

    <p v-if="props.activeVersion.ingredients.length === 0">No ingredients yet.</p>
    <div v-else>
      <div
        v-for="group in groupedActiveIngredients"
        :key="group.grouping || 'ungrouped'"
        class="ingredient-group"
      >
        <h4 v-if="group.grouping">{{ group.grouping }}</h4>
        <ul>
          <li v-for="ingredient in group.ingredients" :key="ingredient.id">
            <div v-if="props.editingIngredientIds[ingredient.id]" class="ingredient-edit-row">
              <input
                v-model="props.ingredientEditDrafts[ingredient.id].name"
                type="text"
                placeholder="Ingredient name"
              />
              <input
                v-model.number="props.ingredientEditDrafts[ingredient.id].amount"
                min="0.01"
                step="0.01"
                type="number"
              />
              <select v-model="props.ingredientEditDrafts[ingredient.id].amount_type">
                <option
                  v-for="amountType in props.amountTypes"
                  :key="`existing-${ingredient.id}-${amountType}`"
                  :value="amountType"
                >
                  {{ amountTypeLabel(amountType) }}
                </option>
              </select>
              <input
                v-model="props.ingredientEditDrafts[ingredient.id].grouping"
                type="text"
                placeholder="Grouping"
              />
              <button
                type="button"
                :disabled="props.savingIngredientId !== ''"
                @click="$emit('save-ingredient', ingredient)"
              >
                {{
                  props.savingIngredientId === ingredient.id ? "Saving..." : "Save"
                }}
              </button>
              <button type="button" @click="$emit('cancel-edit', ingredient.id)">
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
                  <div class="item-actions">
                    <button
                      v-if="!props.showingIngredientNoteForms[ingredient.id]"
                      type="button"
                      class="icon-button compact-button"
                      aria-label="Add note"
                      @click="$emit('show-note-form', ingredient.id)"
                    >
                      💭
                    </button>
                    <button
                      type="button"
                      class="icon-button"
                      aria-label="Edit ingredient"
                      @click="$emit('begin-edit', ingredient)"
                    >
                      ✎
                    </button>
                    <button
                      type="button"
                      class="icon-button danger-icon-button"
                      :disabled="props.deletingIngredientId !== ''"
                      :aria-label="
                        props.deletingIngredientId === ingredient.id
                          ? 'Deleting ingredient'
                          : 'Delete ingredient'
                      "
                      @click="$emit('remove-ingredient', ingredient.id)"
                    >
                      {{
                        props.deletingIngredientId === ingredient.id
                          ? "Deleting..."
                          : "🗑️"
                      }}
                    </button>
                  </div>
                </div>
                <div v-if="ingredient.notes.length > 0" class="note-stack">
                  <div v-for="note in ingredient.notes" :key="note.id" class="note-callout">
                    <div
                      v-if="props.editingIngredientNoteIds[note.id]"
                      class="note-edit-row"
                    >
                      <input
                        v-model="props.ingredientNoteEditBodies[note.id]"
                        type="text"
                        placeholder="Edit note"
                      />
                      <button
                        type="button"
                        :disabled="props.savingEditedIngredientNoteId !== ''"
                        @click="$emit('save-note', ingredient.id, note.id)"
                      >
                        {{
                          props.savingEditedIngredientNoteId === note.id
                            ? "Saving..."
                            : "Save"
                        }}
                      </button>
                      <button type="button" @click="$emit('cancel-note-edit', note.id)">
                        Cancel
                      </button>
                    </div>
                    <div v-else class="note-callout-row">
                      <span>{{ note.body }}</span>
                      <div class="item-actions">
                        <button
                          type="button"
                          class="icon-button"
                          aria-label="Edit note"
                          @click="$emit('begin-note-edit', note.id, note.body)"
                        >
                          ✎
                        </button>
                        <button
                          type="button"
                          class="icon-button danger-icon-button"
                          :disabled="props.deletingIngredientNoteId !== ''"
                          :aria-label="
                            props.deletingIngredientNoteId === note.id
                              ? 'Deleting note'
                              : 'Delete note'
                          "
                          @click="$emit('remove-note', ingredient.id, note.id)"
                        >
                          {{
                            props.deletingIngredientNoteId === note.id
                              ? "Deleting..."
                              : "🗑️"
                          }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <form
                  v-if="props.showingIngredientNoteForms[ingredient.id]"
                  class="note-form"
                  @submit.prevent="$emit('add-note', ingredient.id)"
                >
                  <input
                    v-model="props.ingredientNoteBodies[ingredient.id]"
                    type="text"
                    placeholder="Add note for next time"
                  />
                  <button
                    type="submit"
                    :aria-label="
                      props.savingIngredientNoteId === ingredient.id
                        ? 'Saving note'
                        : 'Save note'
                    "
                  >
                    {{
                      props.savingIngredientNoteId === ingredient.id ? "Saving..." : "☑"
                    }}
                  </button>
                  <button type="button" @click="$emit('hide-note-form', ingredient.id)">
                    Cancel
                  </button>
                </form>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.section-card {
  padding: 24px;
  background: #fffaf3;
  border: 1px solid #d4c5b4;
}

.ingredient-form {
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
  background: #8f6d50;
  color: white;
  cursor: pointer;
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
  padding: 0;
  background: transparent;
  color: #6f5036;
  border: 0;
}

.danger-icon-button {
  color: #8c2f1d;
}

.compact-button {
  font-size: 12px;
  line-height: 1.2;
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

.item-actions {
  display: flex;
  gap: 8px;
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

.note-callout-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.note-edit-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.note-form {
  display: flex;
  gap: 12px;
}

ul {
  padding-left: 20px;
}
</style>
