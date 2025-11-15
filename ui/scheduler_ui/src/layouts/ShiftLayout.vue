<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Page-specific toolbar -->
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" aria-label="Back" @click="goBack" />
        <q-toolbar-title>{{ title }}</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ref } from 'vue';

const router = useRouter();
const title = ref('Shift Management');

function goBack() {
  router.go(-1);
}
</script>
