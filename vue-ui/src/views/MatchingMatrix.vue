<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getMatchingMatrix, apiUrl } from "@/api/api";

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
    <template v-if="matchingMatrixResult">
      <img
        :width="matchingMatrixResult.image1.width"
        :height="matchingMatrixResult.image1.height"
        :src="`${apiUrl}/${matchingMatrixResult.image1.path}`"
        alt="image 1"
      />
      <img
        :width="matchingMatrixResult.image2.width"
        :height="matchingMatrixResult.image2.height"
        :src="`${apiUrl}/${matchingMatrixResult.image2.path}`"
        alt="image 2"
      />
    </template>
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
