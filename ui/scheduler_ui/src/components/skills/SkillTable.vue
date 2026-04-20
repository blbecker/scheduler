<template>
  <q-card bordered class="q-pa-md">
    <q-table
      :rows="skills"
      title="Skills"
      :columns="columns"
      row-key="id"
      :loading="loading"
      flat
      bordered
      dense
    >
      <!-- Top slot: Actions and controls -->
      <template v-slot:top-right>
        <div class="row justify-end q-mb-sm">
          <q-btn color="primary" label="Add Skill" icon="add" @click="onAddSkill" />
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td align="right">
          <q-btn flat dense icon="edit" @click="onEditSkill(props.row)" />
          <q-btn flat dense icon="delete" color="negative" @click="deleteSkill(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!-- Add Skill Form (self-contained modal) -->
    <SkillAddForm v-model="showAddSkillDialog" @saved="handleSkillSaved" />

    <!-- Update Skill Form (self-contained modal) -->
    <SkillUpdateForm
      v-model="showEditSkillDialog"
      :skill="skillBeingEdited"
      v-if="skillBeingEdited"
      @saved="handleSkillUpdated"
    />
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { SkillRead } from 'src/models/skill';
import type { QTableColumn } from 'quasar';
import SkillAddForm from './SkillAddForm.vue';
import { SkillsService } from 'src/services/skillService';
import SkillUpdateForm from './SkillUpdateForm.vue';

const skills = ref<SkillRead[]>([]);
const loading = ref(false);

const showAddSkillDialog = ref(false);
const showEditSkillDialog = ref(false);
const skillBeingEdited = ref<SkillRead | null>(null);

const columns: QTableColumn[] = [
  { name: 'name', label: 'Skill Name', field: 'name', sortable: true },
  { name: 'actions', label: 'Actions', field: 'actions', sortable: false },
];

const fetchSkills = async () => {
  loading.value = true;
  try {
    skills.value = await SkillsService.getSkills();
  } finally {
    loading.value = false;
  }
};

const onAddSkill = () => {
  // Open your SkillAddPage, or a dialog with SkillForm
  console.log('Add Skill clicked');
  showAddSkillDialog.value = true;
};

const onEditSkill = (skill: SkillRead) => {
  skillBeingEdited.value = skill;
  showEditSkillDialog.value = true;
};

const deleteSkill = async (skill: SkillRead) => {
  try {
    await SkillsService.deleteSkill(skill.id);
    // Option 1: re-fetch table
    await fetchSkills();
    // Option 2: remove from array instead of re-fetch
    // skills.value = skills.value.filter(s => s.id !== skill.id)
  } catch (err) {
    console.error(err);
  }
};

const handleSkillSaved = async (newSkill: SkillRead) => {
  // Emit an event or call a method to save the new skill
  console.log('Saving new skill:', newSkill);
  showAddSkillDialog.value = false;
  await fetchSkills(); // refresh table automatically
};

const handleSkillUpdated = async (updatedSkill: SkillRead) => {
  console.log('Edited skill:', updatedSkill);
  showEditSkillDialog.value = false;
  await fetchSkills(); // refresh table after update
};
onMounted(fetchSkills);
</script>
