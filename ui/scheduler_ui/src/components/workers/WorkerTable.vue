<template>
  <q-card bordered class="q-pa-md">
    <q-table :rows="workers" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
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
import type { Worker } from 'src/models/worker';
import type { QTableColumn } from 'quasar';

interface Props {
  workers: Worker[];
  loading?: boolean;
}

const { workers, loading: loadingProp } = defineProps<Props>();
const loading = loadingProp || false;

const columns: QTableColumn[] = [
  { name: 'name', label: 'Name', field: 'name', sortable: true },
  { name: 'email', label: 'Email', field: 'email', sortable: true },
  { name: 'birthdate', label: 'Birthdate', field: 'birthdate', sortable: true },
  { name: 'phone', label: 'Phone', field: 'phone', sortable: false },
  { name: 'actions', label: 'Actions', field: 'actions', sortable: false },
];
</script>
