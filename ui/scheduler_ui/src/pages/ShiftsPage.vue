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

# Add logging to this function so that I can debug client connections AI!
<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { getShifts } from 'src/services/schedulerService';
import type { Shift } from 'src/services/schedulerService';
export default defineComponent({
  setup() {
    const shifts = ref<Shift[]>([]);
    onMounted(async () => {
      console.log('Got shifts');
      shifts.value = await getShifts();
    });

    return { shifts };
  },
});
</script>
