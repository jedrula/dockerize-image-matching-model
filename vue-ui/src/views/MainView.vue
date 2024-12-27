<script setup lang="ts">
import { ref, nextTick, computed } from "vue";
import { findMatchingMatrix, apiUrl } from "@/api/api";

const matchingMatrixResult = ref(null);
const errorMessage = ref("");
const image1 = ref(null);
const image2 = ref(null);
const svgWidth = ref(0);
const svgHeight = ref(0);
const file1 = ref<File | null>(null);
const selectedFolder = ref("");
const image1Url = ref("");

const handleFileChange1 = (event: Event) => {
  const fileInput = event.target as HTMLInputElement;
  file1.value = fileInput.files?.[0] || null;
  if (file1.value) {
    image1Url.value = URL.createObjectURL(file1.value);
  }
};

const uploadFileAndFolder = async () => {
  if (!file1.value || !selectedFolder.value) {
    errorMessage.value = "Please select a file and a folder.";
    return;
  }

  try {
    matchingMatrixResult.value = await findMatchingMatrix(
      file1.value,
      selectedFolder.value,
      () => {}
    );
    await nextTick();
    updateSvgDimensions();
  } catch (error) {
    errorMessage.value =
      "An error occurred while uploading the file and folder.";
    console.error(error);
  }
};

const updateSvgDimensions = () => {
  if (image1.value && image2.value) {
    svgWidth.value = image1.value.width + image2.value.width;
    svgHeight.value = Math.max(image1.value.height, image2.value.height);
  }
};

const lines = computed(() => {
  if (!matchingMatrixResult.value) return [];
  return matchingMatrixResult.value.matched_points.map((match) => {
    const { point1, point2 } = match;
    return {
      x1: point1.x,
      y1: point1.y,
      x2: point2.x + image1.value.width,
      y2: point2.y,
      color: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
      show: ref(false),
      hovered: ref(false),
    };
  });
});

const shownLines = computed(() =>
  lines.value.filter((line) => line.show.value || line.hovered.value)
);

const circleClicked = (line) => {
  console.log("circle clicked", line);
  line.show.value = !line.show.value;
};
</script>

<template>
  <div class="matching-matrix">
    <h1>Find Match</h1>
    <div v-if="errorMessage">{{ errorMessage }}</div>
    <div class="file-inputs">
      <input type="file" @change="handleFileChange1" />
      <select v-model="selectedFolder">
        <option disabled value="">Select Folder</option>
        <option value="szczytna_widokowa">szczytna_widokowa</option>
        <option value="stokowka">stokowka</option>
      </select>
      <button @click="uploadFileAndFolder">Submit</button>
    </div>
    <div class="images-container">
      <img
        ref="image1"
        v-if="image1Url"
        :width="matchingMatrixResult?.image1?.width ?? 'auto'"
        :height="matchingMatrixResult?.image1?.height ?? 'auto'"
        :src="image1Url"
        alt="image 1"
      />
      <img
        ref="image2"
        v-if="matchingMatrixResult?.image2"
        :width="matchingMatrixResult?.image2?.width ?? 'auto'"
        :height="matchingMatrixResult?.image2?.height ?? 'auto'"
        :src="`${apiUrl}/${matchingMatrixResult.image2.path}`"
        alt="image 2"
      />
      <div
        class="svg-wrapper"
        :style="{ width: svgWidth + 'px', height: svgHeight + 'px' }"
      >
        <svg :width="svgWidth" :height="svgHeight">
          <template v-if="svgWidth && svgHeight">
            <template v-for="(line, index) in lines" :key="`circle-${index}`">
              <circle
                :cx="line.x1"
                :cy="line.y1"
                r="6"
                :fill="line.color"
                @click="circleClicked(line)"
                @mouseover="line.hovered.value = true"
                @mouseleave="line.hovered.value = false"
                :class="{ shown: line.show.value }"
              />
              <circle
                :cx="line.x2"
                :cy="line.y2"
                r="6"
                :fill="line.color"
                @click="circleClicked(line)"
                @mouseover="line.hovered.value = true"
                @mouseleave="line.hovered.value = false"
                :class="{ shown: line.show.value }"
              />
            </template>
            <line
              v-for="(line, index) in shownLines"
              :key="`line-${index}`"
              :x1="line.x1"
              :y1="line.y1"
              :x2="line.x2"
              :y2="line.y2"
              :stroke="line.color"
              stroke-width="3"
              @mouseover="line.hovered.value = true"
              @mouseleave="line.hovered.value = false"
            />
          </template>
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.matching-matrix {
  padding: 20px;
  background-color: #fff;
  border-radius: 5px;
}

.file-inputs {
  margin-bottom: 20px;
}

.images-container {
  position: relative;
  display: flex;
}

.svg-wrapper {
  position: absolute;
  top: 0;
  left: 0;
}

pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

circle {
  cursor: pointer;
  opacity: 0.5;
}

circle.shown {
  opacity: 1;
}
</style>
