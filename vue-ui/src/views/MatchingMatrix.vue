<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getMatchingMatrix } from "@/api/api";

const matchingMatrixResult = ref(null);
const errorMessage = ref("");

onMounted(async () => {
  try {
    matchingMatrixResult.value = await getMatchingMatrix();
  } catch (error) {
    errorMessage.value =
      "An error occurred while fetching the matching matrix.";
  }
});
</script>

<template>
  <div class="matching-matrix">
    <h1>Matching Matrix</h1>
    <div v-if="errorMessage">{{ errorMessage }}</div>
    <pre v-if="matchingMatrixResult">{{
      JSON.stringify(matchingMatrixResult, null, 2)
    }}</pre>
  </div>
</template>

<style scoped>
.matching-matrix {
  padding: 20px;
  background-color: #fff;
  border-radius: 5px;
}

pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}
</style>
