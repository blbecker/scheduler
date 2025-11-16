<template>
  <q-dialog v-model="show">
    <q-card class="q-pa-md" style="min-width: 350px">
      <h6>Update Skill</h6>
      <q-form @submit.prevent="onSubmit" ref="formRef">
        <!-- Skill Name -->
        <q-input
          filled
          v-model="skill.name"
          label="Skill Name"
          :rules="[(val) => !!val || 'Name is required']"
          ref="nameInput"
        />

        <!-- Form Buttons -->
        <div class="row justify-end q-mt-md">
          <q-btn label="Cancel" flat color="negative" @click="onCancel" />
          <q-btn label="Save" type="submit" color="primary" class="q-ml-sm" />
        </div>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import type { SkillRead, SkillUpdate } from 'src/models/skill';
import { SkillsService } from 'src/services/skillService';

interface Props {
  modelValue: boolean;
  skill: SkillRead; // row from the table being edited
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'saved', skill: SkillRead): void;
  (e: 'canceled'): void;
}>();

const show = ref(props.modelValue);
watch(
  () => props.modelValue,
  (val) => (show.value = val),
);
watch(show, (val) => emit('update:modelValue', val));

// Refs
const formRef = ref();
const nameInput = ref();

// Initialize the reactive form with only editable fields (SkillUpdate)
const skill = reactive<SkillUpdate>({ name: props.skill.name });
watch(
  () => props.skill,
  (newSkill) => {
    if (newSkill) {
      skill.name = newSkill.name; // copy editable fields
    }
  },
  { immediate: true }, // also run once on mount
);

// Focus input on mount
onMounted(() => {
  nameInput.value?.focus();
});

// Submit handler
const onSubmit = async () => {
  const valid = await formRef.value.validate();
  if (!valid) return;

  try {
    // Submit SkillUpdate (id removed)
    const payload: SkillUpdate = { ...skill }; // already only editable fields
    const updated = await SkillsService.updateSkill(props.skill.id, payload);
    emit('saved', updated);
  } catch (err) {
    console.error(err);
  }
};

// Cancel handler
const onCancel = () => {
  show.value = false;
  emit('canceled');
};
</script>
