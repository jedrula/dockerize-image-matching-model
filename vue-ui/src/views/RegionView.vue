<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getRegion, apiUrl } from "@/api/api";
import { useRoute } from "vue-router";

const route = useRoute();

const regionData = ref({});

onMounted(async () => {
  const region = await getRegion(route.params.region);
  console.log(region);
  regionData.value = region;
});
</script>

<template>
  <div>
    <h1>Region</h1>
    <div
      v-for="{ name, path } in regionData"
      :key="path"
      @click="$router.push(`/crag/${route.params.region}/${name}`)"
    >
      <img :src="`${apiUrl}/${path}`" />
      <p>{{ name }}</p>
    </div>
  </div>
</template>

<style scoped>
img {
  width: 300px;
}
</style>
