<template>
  <q-card bordered class="q-pa-md">
    <q-table :rows="skills" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-actions="props">
        <q-td align="right">
          <q-btn flat dense icon="edit" @click="$emit('edit', props.row)" />
          <q-btn flat dense icon="delete" color="negative" @click="$emit('delete', props.row)" />
        </q-td>
      </template>
    </q-table>
  </q-card>
</template>

<script setup lang="ts">
import type { Skill } from 'src/models/skill';
import type { QTableColumn } from 'quasar';

interface Props {
  skills: Skill[];
  loading?: boolean;
}

const { skills, loading: loadingProp } = defineProps<Props>();
const loading = loadingProp || false;

const columns: QTableColumn[] = [
  { name: 'name', label: 'Skill Name', field: 'name', sortable: true },
  { name: 'actions', label: 'Actions', field: 'actions', sortable: false },
];
</script>
