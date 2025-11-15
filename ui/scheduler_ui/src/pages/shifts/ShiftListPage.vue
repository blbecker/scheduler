<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Shift } from 'src/models/shift';
import { ShiftsService } from 'src/services/shiftService';
import ShiftTable from 'components/shifts/ShiftTable.vue';

const shifts = ref<Shift[]>([]);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    shifts.value = await ShiftsService.getShifts();
  } finally {
    loading.value = false;
  }
});

function editShift(row: Shift) {
  console.log('Edit shift:', row);
}

function deleteShift(row: Shift) {
  console.log('Delete shift:', row);
}
</script>

<template>
  <q-page class="q-pa-md">
    <ShiftTable :shifts="shifts" :loading="loading" @edit="editShift" @delete="deleteShift" />
  </q-page>
</template>
