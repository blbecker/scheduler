<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { SkillRead } from 'src/models/skill';
import { SkillsService } from 'src/services/skillService';
import SkillTable from 'components/skills/SkillTable.vue';

const skills = ref<SkillRead[]>([]);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    skills.value = await SkillsService.getSkills();
  } finally {
    loading.value = false;
  }
});

function editSkill(row: SkillRead) {
  console.log('Edit skill:', row);
}

function deleteSkill(row: SkillRead) {
  console.log('Delete skill:', row);
}
</script>

<template>
  <q-page class="q-pa-md">
    <SkillTable :skills="skills" :loading="loading" @edit="editSkill" @delete="deleteSkill" />
  </q-page>
</template>
