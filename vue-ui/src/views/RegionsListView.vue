<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getLocations } from "@/api/api";

const availableLocations = ref([]);

onMounted(async () => {
  availableLocations.value = await getLocations();
});
</script>

<template>
  <div>
    <h1>Regions</h1>
    <ul>
      <li v-for="location in availableLocations" :key="location.id">
        <router-link
          :to="{ name: 'region', params: { region: location.name } }"
        >
          {{ location.label }}
        </router-link>
      </li>
    </ul>
  </div>
</template>
