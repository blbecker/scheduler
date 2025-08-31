<template>
  <q-page>
    <q-list>
      <q-item v-for="shift in shifts" :key="shift.id">
        <q-item-section>{{ shift.title }}</q-item-section>
        <q-item-section>{{ shift.completed ? 'Done' : 'Pending' }}</q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { getShifts } from 'src/services/schedulerService';
import type { Shift } from 'src/services/schedulerService';
export default defineComponent({
  setup() {
    const shifts = ref<Shift[]>([]);
    onMounted(async () => {
      console.log('Fetching shifts...');
      try {
        const fetchedShifts = await getShifts();
        console.log('Successfully fetched shifts:', {
          count: fetchedShifts.length,
          firstShift: fetchedShifts[0] || 'No shifts available',
        });
        shifts.value = fetchedShifts;
      } catch (error) {
        console.error('Failed to fetch shifts:', {
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString(),
        });
        throw error;
      }
    });

    return { shifts };
  },
});
</script>
