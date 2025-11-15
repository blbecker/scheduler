<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Main header -->
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>{{ headerTitle }}</q-toolbar-title>
        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <!-- Side drawer -->
    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header>Essential Links</q-item-label>
        <EssentialLink v-for="link in linksList" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>

    <!-- Main page container: renders child layouts/pages -->
    <q-page-container>
      <router-view />
    </q-page-container>

    <!-- Optional footer -->
    <q-footer elevated>
      <div class="text-center">My App Footer</div>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import EssentialLink, { type EssentialLinkProps } from 'components/EssentialLink.vue';

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

const linksList: EssentialLinkProps[] = [
  { title: 'Shifts', caption: 'View shifts', icon: 'schedule', link: '/shifts' },
  { title: 'Skills', caption: 'View skills', icon: 'construction', link: '/skills' },
  { title: 'Workers', caption: 'View workers', icon: 'person', link: '/workers' },
];

const headerTitle = 'My Quasar App'; // can also be dynamic per route
</script>
