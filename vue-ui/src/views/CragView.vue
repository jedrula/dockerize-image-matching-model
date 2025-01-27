<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getCrag, apiUrl } from "@/api/api";
import { useRoute } from "vue-router";

const route = useRoute();

const image = ref("");
const cragData = ref({
  name: "",
  crags: [],
});

onMounted(async () => {
  console.log("ee");
  const crag = await getCrag(`${route.params.region}/${route.params.crag}`);
  console.log(crag);
  image.value = crag.image;
  cragData.value = { ...cragData.value, ...crag.data };
});
</script>

<template>
  <div>
    <h1>Crag</h1>
    <img :src="`${apiUrl}/${image}`" />
    <h2>Name: {{ cragData.name }}</h2>
    <p>Crags: {{ cragData.crags }}</p>
  </div>
</template>

<style scoped>
img {
  width: 300px;
}
</style>
