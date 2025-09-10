<template>
  <q-page>
    <q-list>
      <q-item v-for="worker in workers" :key="worker.id">
        <q-item-section>{{ worker.name }}</q-item-section>
        <q-item-section>
          <q-badge v-for="skillId in worker.skills" :key="skillId" class="q-mr-xs">
            {{ skillId }}
          </q-badge>
        </q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { getWorkers } from 'src/services/workerService';
import type { Worker } from 'src/services/workerService';
export default defineComponent({
  setup() {
    const workers = ref<Worker[]>([]);
    onMounted(async () => {
      console.log('Fetching workers...');
      try {
        const fetchedWorkers = await getWorkers();
        console.log('Successfully fetched workers:', {
          count: fetchedWorkers.length,
          firstWorker: fetchedWorkers[0] || 'No workers available',
        });
        workers.value = fetchedWorkers;
      } catch (error) {
        console.error('Failed to fetch workers:', {
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString(),
        });
        throw error;
      }
    });

    return { workers };
  },
});
</script>
