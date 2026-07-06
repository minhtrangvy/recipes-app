<script setup lang="ts">
import type {
  ImportedInstructionDraft,
  IngredientAmountType,
  RecipeImportDraft,
} from "../types";

const props = defineProps<{
  importDraft: RecipeImportDraft;
  amountTypes: IngredientAmountType[];
  isApplyingImportDraft: boolean;
}>();

defineEmits<{
  (event: "add-ingredient"): void;
  (event: "remove-ingredient", index: number): void;
  (event: "add-instruction"): void;
  (event: "remove-instruction", index: number): void;
  (event: "add-step", instruction: ImportedInstructionDraft): void;
  (event: "remove-step", instruction: ImportedInstructionDraft, index: number): void;
  (event: "apply"): void;
  (event: "cancel"): void;
}>();

function amountTypeLabel(amountType: IngredientAmountType) {
  if (amountType === "weight_g") {
    return "grams";
  }

  return amountType;
}
</script>

<template>
  <div class="section-card">
    <div class="section-header">
      <h3>Import review</h3>
      <button type="button" @click="$emit('add-ingredient')">Add ingredient</button>
    </div>

    <div
      v-for="(ingredient, ingredientIndex) in props.importDraft.ingredients"
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
          v-for="amountType in props.amountTypes"
          :key="`draft-amount-${amountType}`"
          :value="amountType"
        >
          {{ amountTypeLabel(amountType) }}
        </option>
      </select>
      <button
        type="button"
        class="danger-button"
        @click="$emit('remove-ingredient', ingredientIndex)"
      >
        Remove
      </button>
    </div>

    <div class="section-header">
      <h3>Instructions</h3>
      <button type="button" @click="$emit('add-instruction')">Add instruction</button>
    </div>

    <div
      v-for="(instruction, instructionIndex) in props.importDraft.instructions"
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
          @click="$emit('remove-instruction', instructionIndex)"
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
          @click="$emit('remove-step', instruction, stepIndex)"
        >
          Remove step
        </button>
      </div>

      <button type="button" @click="$emit('add-step', instruction)">Add step</button>
    </div>

    <div class="draft-actions">
      <button type="button" :disabled="props.isApplyingImportDraft" @click="$emit('apply')">
        {{ props.isApplyingImportDraft ? "Saving..." : "Save imported data" }}
      </button>
      <button type="button" class="danger-button" @click="$emit('cancel')">
        Cancel
      </button>
    </div>
  </div>
</template>

<style scoped>
.section-card {
  padding: 24px;
  background: #fffaf3;
  border: 1px solid #d4c5b4;
  border-radius: 12px;
}

.section-header {
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

.instruction-card + .instruction-card {
  margin-top: 20px;
}

.draft-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
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
  border-radius: 10px;
  background: white;
}

button {
  padding: 10px 16px;
  border: 0;
  background: #8f6d50;
  color: white;
  cursor: pointer;
}

.danger-button {
  background: #8c2f1d;
}
</style>
