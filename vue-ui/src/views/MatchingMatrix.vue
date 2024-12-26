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
        <canvas
          ref="canvas"
          :width="canvasWidth"
          :height="canvasHeight"
        ></canvas>
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
const canvas = ref(null);
const image1 = ref(null);
const image2 = ref(null);
const canvasWidth = ref(0);
const canvasHeight = ref(0);

onMounted(async () => {
  try {
    matchingMatrixResult.value = await getMatchingMatrix();
    await nextTick();
    const ctx = canvas.value.getContext("2d");
    drawLines(ctx);
  } catch (error) {
    errorMessage.value =
      "An error occurred while fetching the matching matrix.";
  }
});

const drawLines = async (ctx) => {
  if (!ctx || !image1.value || !image2.value || !matchingMatrixResult.value)
    return;

  canvasWidth.value = image1.value.width + image2.value.width;
  canvasHeight.value = Math.max(image1.value.height, image2.value.height);

  await nextTick();

  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value);
  ctx.lineWidth = 3;

  // let's scale coordinates by widths of corresponding images
  matchingMatrixResult.value.matched_points.forEach((match) => {
    const { point1, point2 } = match;
    ctx.beginPath();
    // let's make stroke style differnt in each iteration
    ctx.strokeStyle = `#${Math.floor(Math.random() * 16777215).toString(16)}`;
    console.log("1", point1.x, point1.y);
    ctx.moveTo(point1.x, point1.y);
    console.log("2", point2.x + image1.value.width, point2.y);
    ctx.lineTo(point2.x + image1.value.width, point2.y);
    ctx.stroke();
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

canvas {
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
