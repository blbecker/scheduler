<template>
  <q-card bordered class="q-pa-md">
    <q-table :rows="shifts" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
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
import type { Shift } from 'src/models/shift';
import type { QTableColumn } from 'quasar';

interface Props {
  shifts: Shift[];
  loading?: boolean;
}

const { shifts, loading: loadingProp } = defineProps<Props>();
const loading = loadingProp || false;

const columns: QTableColumn[] = [
  { name: 'id', label: 'Shift ID', field: 'id', sortable: true },
  { name: 'start_time', label: 'Start Time', field: 'start_time', sortable: true },
  { name: 'end_time', label: 'End Time', field: 'end_time', sortable: true },
  { name: 'actions', label: 'Actions', field: 'actions', sortable: false },
];
</script>
