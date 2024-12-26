<template>
  <div class="matching-matrix">
    <h1>Matching Matrix</h1>
    <div v-if="errorMessage">{{ errorMessage }}</div>
    <template v-if="matchingMatrixResult">
      <div class="images-container">
        <img
          ref="image1"
          :width="matchingMatrixResult.image1.width"
          :height="matchingMatrixResult.image1.height"
          :src="`${apiUrl}/${matchingMatrixResult.image1.path}`"
          alt="image 1"
        />
        <img
          ref="image2"
          :width="matchingMatrixResult.image2.width"
          :height="matchingMatrixResult.image2.height"
          :src="`${apiUrl}/${matchingMatrixResult.image2.path}`"
          alt="image 2"
        />
        <svg ref="svg" :width="svgWidth" :height="svgHeight"></svg>
      </div>
      <pre>{{
        JSON.stringify(matchingMatrixResult.matched_points, null, 2)
      }}</pre>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue";
import { getMatchingMatrix, apiUrl } from "@/api/api";

const matchingMatrixResult = ref(null);
const errorMessage = ref("");
const svg = ref(null);
const image1 = ref(null);
const image2 = ref(null);
const svgWidth = ref(0);
const svgHeight = ref(0);

onMounted(async () => {
  try {
    matchingMatrixResult.value = await getMatchingMatrix();
    await nextTick();
    drawLines();
  } catch (error) {
    errorMessage.value =
      "An error occurred while fetching the matching matrix.";
  }
});

const drawLines = async () => {
  if (
    !svg.value ||
    !image1.value ||
    !image2.value ||
    !matchingMatrixResult.value
  )
    return;

  svgWidth.value = image1.value.width + image2.value.width;
  svgHeight.value = Math.max(image1.value.height, image2.value.height);

  await nextTick();

  const svgElement = svg.value;
  svgElement.innerHTML = ""; // Clear previous lines

  matchingMatrixResult.value.matched_points.forEach((match) => {
    const { point1, point2 } = match;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", point1.x);
    line.setAttribute("y1", point1.y);
    line.setAttribute("x2", point2.x + image1.value.width);
    line.setAttribute("y2", point2.y);
    line.setAttribute(
      "stroke",
      `#${Math.floor(Math.random() * 16777215).toString(16)}`
    );
    line.setAttribute("stroke-width", "3");
    svgElement.appendChild(line);
  });
};
</script>

<style scoped>
.matching-matrix {
  padding: 20px;
  background-color: #fff;
  border-radius: 5px;
}

.images-container {
  position: relative;
  display: flex;
}

svg {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}
</style>
