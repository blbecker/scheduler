<template>
  <q-page>
    <q-list>
      <q-item v-for="skill in skills" :key="skill.id">
        <q-item-section>{{ skill.name }}</q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { getSkills } from 'src/services/skillService';
import type { Skill } from 'src/services/skillService';
export default defineComponent({
  setup() {
    const skills = ref<Skill[]>([]);
    onMounted(async () => {
      console.log('Fetching skills...');
      try {
        const fetchedSkills = await getSkills();
        console.log('Successfully fetched skills:', {
          count: fetchedSkills.length,
          firstSkill: fetchedSkills[0] || 'No skills available',
        });
        skills.value = fetchedSkills;
      } catch (error) {
        console.error('Failed to fetch skills:', {
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString(),
        });
        throw error;
      }
    });

    return { skills };
  },
});
</script>
