<template>
  <q-page padding>
    <div v-if="loading" class="text-center q-mt-lg">
      <q-spinner color="primary" size="3em" />
      <div class="q-mt-sm">Loading shift details...</div>
    </div>

    <div v-else-if="error" class="text-negative q-pa-md">Error loading shift: {{ error }}</div>

    <div v-else-if="shift" class="q-pa-md">
      <h2 class="text-h4">Shift Details</h2>

      <q-card class="q-mt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6">
              <q-item>
                <q-item-section>
                  <q-item-label caption>ID</q-item-label>
                  <q-item-label>{{ shift.id }}</q-item-label>
                </q-item-section>
              </q-item>
            </div>
            <div class="col-12 col-sm-6">
              <q-item>
                <q-item-section>
                  <q-item-label caption>Status</q-item-label>
                  <q-item-label>{{ shift.reversed_id }}</q-item-label>
                  <q-item-label>{{ shift.flerp }}</q-item-label>
                </q-item-section>
              </q-item>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { api } from 'src/boot/axios';

import { Shift } from 'src/components/models';

const route = useRoute();

const shiftId = computed(() => {
  const id = route.params.id;
  if (Array.isArray(id)) {
    return id[0]; // Take first element if it's an array
  }
  return id || ''; // Fallback to empty string if undefined
});

const shift = ref<Shift | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    console.log('Loading shift details for ID:', route.params.id);
    const response = await api.get(`v1/shift/${shiftId.value}`);
    shift.value = response.data;
    console.log('Loaded shift:', shift.value);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load shift';
    console.error('Error loading shift:', err);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
