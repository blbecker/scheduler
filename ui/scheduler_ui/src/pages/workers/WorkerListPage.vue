<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Worker } from 'src/models/worker';
import { WorkersService } from 'src/services/workerService';
import WorkerTable from 'components/workers/WorkerTable.vue';

const workers = ref<Worker[]>([]);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    workers.value = await WorkersService.getWorkers();
  } finally {
    loading.value = false;
  }
});

function editWorker(row: Worker) {
  console.log('Edit worker:', row);
}

function deleteWorker(row: Worker) {
  console.log('Delete worker:', row);
}
</script>

<template>
  <q-page class="q-pa-md">
    <WorkerTable :workers="workers" :loading="loading" @edit="editWorker" @delete="deleteWorker" />
  </q-page>
</template>
