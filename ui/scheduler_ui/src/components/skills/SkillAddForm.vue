<template>
  <q-dialog v-model="show">
    <q-card class="q-pa-md" style="min-width: 350px">
      <q-card-section class="q-pt-none q-pb-sm">
        <h6>Add New Skill</h6>
        <q-form @submit="onSubmit" ref="formRef">
          <q-input
            filled
            v-model="skill.name"
            label="Skill Name"
            :rules="[(val) => !!val || 'Name is required']"
            ref="nameInput"
            class="q-mb-sm"
          />

          <div class="row justify-end q-mt-md">
            <q-btn flat label="Cancel" color="negative" @click="emitCancel" />
            <q-btn label="Save Skill" type="submit" color="primary" />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { SkillCreate, SkillRead } from 'src/models/skill';
import { newSkillCreate } from 'src/models/skill';
import { SkillsService } from 'src/services/skillService';

interface Props {
  modelValue: boolean;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'saved', skill: SkillRead): void;
  (e: 'canceled'): void;
}

const emit = defineEmits<Emits>();

const show = ref(props.modelValue);
watch(
  () => props.modelValue,
  (val) => (show.value = val),
);
watch(show, (val) => emit('update:modelValue', val));

const formRef = ref();
const nameInput = ref();
const skill = ref<SkillCreate>(newSkillCreate());

const onSubmit = async () => {
  const valid = await formRef.value.validate();
  if (!valid) return;

  try {
    const created = await SkillsService.createSkill(skill.value);
    emit('saved', created);
    skill.value = newSkillCreate();
  } catch (err) {
    console.error(err);
  }
};

const emitCancel = () => {
  emit('canceled');
};

onMounted(() => {
  nameInput.value?.focus();
});
</script>
