<script setup lang="ts">
import type { RecipeVersion } from "../types";

const props = defineProps<{
  activeVersion: RecipeVersion;
  instructionTitle: string;
  isSavingInstruction: boolean;
  deletingInstructionId: string;
  stepBodies: Record<string, string>;
  savingStepInstructionId: string;
  editingStepIds: Record<string, boolean>;
  stepEditBodies: Record<string, string>;
  savingEditedStepId: string;
  deletingStepId: string;
  showingStepNoteForms: Record<string, boolean>;
  stepNoteBodies: Record<string, string>;
  savingStepNoteId: string;
}>();

defineEmits<{
  (event: "update:instructionTitle", value: string): void;
  (event: "add-instruction"): void;
  (event: "remove-instruction", instructionId: string): void;
  (event: "add-step", instructionId: string): void;
  (event: "begin-step-edit", stepId: string, body: string): void;
  (event: "save-step", instructionId: string, stepId: string): void;
  (event: "cancel-step-edit", stepId: string): void;
  (event: "remove-step", instructionId: string, stepId: string): void;
  (event: "show-note-form", stepId: string): void;
  (event: "add-note", stepId: string): void;
  (event: "hide-note-form", stepId: string): void;
}>();
</script>

<template>
  <div class="section-card">
    <div class="section-header">
      <h3>Instructions</h3>
    </div>

    <form class="instruction-form" @submit.prevent="$emit('add-instruction')">
      <input
        :value="props.instructionTitle"
        type="text"
        placeholder="Instruction title (optional)"
        @input="$emit('update:instructionTitle', ($event.target as HTMLInputElement).value)"
      />
      <button
        type="submit"
        :aria-label="props.isSavingInstruction ? 'Saving instruction' : 'Add instruction'"
      >
        {{ props.isSavingInstruction ? "Saving..." : "➕📄" }}
      </button>
    </form>

    <p v-if="props.activeVersion.instructions.length === 0">No instructions yet.</p>
    <div
      v-else
      v-for="instruction in props.activeVersion.instructions"
      :key="instruction.id"
      class="instruction-card"
    >
      <div class="instruction-header">
        <h4 v-if="instruction.title">{{ instruction.title }}</h4>
        <button
          type="button"
          class="danger-button"
          :disabled="props.deletingInstructionId !== ''"
          :aria-label="
            props.deletingInstructionId === instruction.id
              ? 'Deleting instruction'
              : 'Delete instruction'
          "
          @click="$emit('remove-instruction', instruction.id)"
        >
          {{
            props.deletingInstructionId === instruction.id ? "Deleting..." : "🗑️📄"
          }}
        </button>
      </div>
      <ol v-if="instruction.steps.length > 0">
        <li v-for="step in instruction.steps" :key="step.id">
          <div class="item-with-note">
            <div v-if="props.editingStepIds[step.id]" class="step-edit-row">
              <input
                v-model="props.stepEditBodies[step.id]"
                type="text"
                placeholder="Step"
              />
              <button
                type="button"
                :disabled="props.savingEditedStepId !== ''"
                @click="$emit('save-step', instruction.id, step.id)"
              >
                {{
                  props.savingEditedStepId === step.id ? "Saving..." : "Save"
                }}
              </button>
              <button type="button" @click="$emit('cancel-step-edit', step.id)">
                Cancel
              </button>
            </div>
            <div v-else class="step-row">
              <span>{{ step.body }}</span>
              <div class="item-actions">
                <button
                  v-if="!props.showingStepNoteForms[step.id]"
                  type="button"
                  class="icon-button compact-button"
                  aria-label="Add note"
                  @click="$emit('show-note-form', step.id)"
                >
                  💭
                </button>
                    <button
                      type="button"
                      class="icon-button"
                      aria-label="Edit step"
                      @click="$emit('begin-step-edit', step.id, step.body)"
                    >
                      ✎
                    </button>
                    <button
                      type="button"
                      class="danger-button"
                      :disabled="props.deletingStepId !== ''"
                  :aria-label="
                    props.deletingStepId === step.id ? 'Deleting step' : 'Delete step'
                  "
                  @click="$emit('remove-step', instruction.id, step.id)"
                >
                  {{ props.deletingStepId === step.id ? "Deleting..." : "🗑️" }}
                </button>
              </div>
            </div>
            <div v-if="step.notes.length > 0" class="note-stack">
              <div v-for="note in step.notes" :key="note.id" class="note-callout">
                {{ note.body }}
              </div>
            </div>
            <form
              v-if="props.showingStepNoteForms[step.id]"
              class="note-form"
              @submit.prevent="$emit('add-note', step.id)"
            >
              <input
                v-model="props.stepNoteBodies[step.id]"
                type="text"
                placeholder="Add note for next time"
              />
              <button
                type="submit"
                :aria-label="
                  props.savingStepNoteId === step.id ? 'Saving note' : 'Save note'
                "
              >
                {{ props.savingStepNoteId === step.id ? "Saving..." : "☑" }}
              </button>
              <button type="button" @click="$emit('hide-note-form', step.id)">
                Cancel
              </button>
            </form>
          </div>
        </li>
      </ol>
      <p v-else>No steps yet.</p>

      <form class="instruction-form" @submit.prevent="$emit('add-step', instruction.id)">
        <input
          v-model="props.stepBodies[instruction.id]"
          type="text"
          placeholder="Add step"
        />
        <button
          type="submit"
          :aria-label="
            props.savingStepInstructionId === instruction.id ? 'Saving step' : 'Add step'
          "
        >
          {{ props.savingStepInstructionId === instruction.id ? "Saving..." : "➕" }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.section-card {
  padding: 24px;
  background: #fffaf3;
  border: 1px solid #d4c5b4;
}

.section-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.instruction-form {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

input,
button {
  font: inherit;
}

input {
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

.danger-button {
  background: #8c2f1d;
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

.step-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.step-edit-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.item-with-note {
  display: grid;
  gap: 10px;
}

.item-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.icon-button {
  padding: 4px 8px;
  background: transparent;
  color: #6f5036;
  border: 1px solid #a99987;
}

.compact-button {
  font-size: 12px;
  line-height: 1.2;
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
</style>
