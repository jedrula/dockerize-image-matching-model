<script setup lang="ts">
import { ref } from "vue";
import { createRegion } from "@/api/api";
import { useRouter } from "vue-router";

const name = ref("");
const router = useRouter();

const onSave = async () => {
  await createRegion({
    region_name: name.value,
  });
  if (name.value) {
    router.push(`/region/${name.value}`);
  }
};
</script>

<template>
  <div>
    <h1>Add Region</h1>
    <input type="text" v-model="name" placeholder="Enter name" />
    <button @click="onSave">Save</button>
  </div>
</template>
