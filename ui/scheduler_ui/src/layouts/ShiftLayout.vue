<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" aria-label="Back" @click="goBack" />

        <q-toolbar-title>Shift Management</q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view v-slot="{ Component }">
        <component :is="Component" />
        <div v-if="!Component" class="text-negative">
          No shift component matched the route!
        </div>
      </router-view>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

function goBack() {
  router.go(-1);
}
</script>

<style scoped>
/* Add any specific styles for shift management here */
</style>
