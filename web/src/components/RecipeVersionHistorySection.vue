<script setup lang="ts">
import type { RecipeVersion } from "../types";

const props = defineProps<{
  versions: RecipeVersion[];
  isVersionHistoryVisible: boolean;
  isCreatingVersion: boolean;
  deletingVersionId: string;
}>();

defineEmits<{
  (event: "toggle"): void;
  (event: "add-version"): void;
  (event: "remove-version", versionId: string): void;
}>();
</script>

<template>
  <div class="section-card">
    <div class="section-header">
      <h3>Version History</h3>
      <button type="button" @click="$emit('toggle')">
        {{ props.isVersionHistoryVisible ? "Hide" : "Show" }}
      </button>
    </div>

    <div v-if="props.isVersionHistoryVisible">
      <div class="section-header">
        <h4>Versions</h4>
        <button type="button" @click="$emit('add-version')">
          {{ props.isCreatingVersion ? "Adding..." : "Add version" }}
        </button>
      </div>

      <p v-if="props.versions.length === 0">No versions yet.</p>

      <ul v-else>
        <li v-for="version in props.versions" :key="version.id">
          <div class="version-row">
            <span>
              V{{ version.version_number }} ·
              {{ version.ingredient_count }} ingredients
            </span>
            <button
              type="button"
              class="danger-button"
              :disabled="props.versions.length === 1 || props.deletingVersionId !== ''"
              @click="$emit('remove-version', version.id)"
            >
              {{
                props.deletingVersionId === version.id ? "Deleting..." : "Delete version"
              }}
            </button>
          </div>
        </li>
      </ul>
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

button {
  padding: 10px 16px;
  border: 0;
  background: #8f6d50;
  color: white;
  cursor: pointer;
  font: inherit;
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
</style>
