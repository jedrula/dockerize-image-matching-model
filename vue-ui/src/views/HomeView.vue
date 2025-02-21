<script setup lang="ts">
import { ref, onMounted } from "vue";
import {
  findMatch,
  getBestMatchPreview,
  getLocations,
  apiUrl,
} from "@/api/api";

const progressBarWidth = ref(0);
const resultMessage = ref("");
const selectedFolder = ref("");
const file = ref<File | null>(null);
const bestMatch = ref(""); // ./images/szczytna/widokowa/widokowa2.png
const bestMatchScore = ref(0);
const allScores = ref<Record<string, number>>({});
const bestMatchPreviewUrl = ref("");
const availableLocations = ref([]);

const onUploadProgress = (progressEvent: AxiosProgressEvent) => {
  progressBarWidth.value = Math.round(
    progressEvent.total ? (progressEvent.loaded * 100) / progressEvent.total : 0
  );
};

async function requestBestMatchPreview(file: File, bestMatch: string) {
  try {
    const response = await getBestMatchPreview(
      file,
      bestMatch,
      onUploadProgress
    );
    bestMatchPreviewUrl.value = URL.createObjectURL(response.data);
  } catch (error) {
    console.error(error);
    resultMessage.value = "An error occurred!";
  }
}

async function uploadFile() {
  if (!file.value || !selectedFolder.value) {
    resultMessage.value = "Please select a file and a folder.";
    return;
  }

  try {
    const data = await findMatch(
      file.value,
      selectedFolder.value,
      onUploadProgress
    );
    bestMatch.value = data.best_match;
    bestMatchScore.value = data.score;
    allScores.value = data.all_scores;
    resultMessage.value = "";
    requestBestMatchPreview(file.value, data.best_match);
  } catch (error) {
    console.error(error);
    resultMessage.value = "An error occurred!";
  }
}

function handleFileChange(event: Event) {
  const fileInput = event.target as HTMLInputElement;
  file.value = fileInput.files?.[0] || null;
}

onMounted(async () => {
  try {
    availableLocations.value = await getLocations();
  } catch (error) {
    console.error("Error fetching locations:", error);
  }
});
</script>

<template>
  <div class="container">
    <div class="progress">
      <div
        id="progress-bar"
        class="progress-bar"
        :style="{ width: progressBarWidth + '%' }"
      ></div>
    </div>

    <div class="file-input">
      <input type="file" id="file-input" @change="handleFileChange" />
      <label for="file-input">Choose Image</label>
    </div>

    <div class="folder-select">
      <select v-model="selectedFolder">
        <option disabled value="">Select Folder</option>
        <option
          v-for="location in availableLocations"
          :key="location.name"
          :value="location.name"
        >
          {{ location.label }}
        </option>
      </select>
    </div>

    <button @click="uploadFile">Submit</button>

    <div id="result" class="result">
      <p v-if="resultMessage">{{ resultMessage }}</p>
      <div v-if="bestMatch">
        <h2>
          Best Match <small>(score {{ bestMatchScore }})</small>
        </h2>
        <p>{{ bestMatch }}</p>
        <!-- best match img -->
        <img
          v-if="bestMatch"
          :src="`${apiUrl}/${bestMatch}`"
          alt="Best Match"
        />
        <div v-if="bestMatchPreviewUrl">
          <img :src="bestMatchPreviewUrl" alt="Best Match Preview" />
        </div>
        <h2>All Scores</h2>
        <ul>
          <li v-for="(score, key) in allScores" :key="key">
            {{ key }}: {{ score }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f4f4f4;
}

.container {
  width: 80%;
  margin: 0 auto;
  overflow: hidden;
}

.progress {
  width: 100%;
  background-color: #f4f4f4;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin: 20px 0;
}

.progress-bar {
  width: 0;
  height: 20px;
  background-color: #007bff;
  color: #fff;
  text-align: center;
  line-height: 20px;
}

.file-input {
  margin: 20px 0;
}

.file-input input[type="file"] {
  display: none;
}

.file-input label {
  background-color: #007bff;
  color: #fff;
  text-align: center;
  padding: 10px;
  border-radius: 5px;
  cursor: pointer;
}

.file-input label:hover {
  background-color: #0056b3;
}

.folder-select {
  margin: 20px 0;
}

.folder-select select {
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

button {
  background-color: #007bff;
  color: #fff;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.result {
  margin: 20px 0;
  padding: 20px;
  background-color: #fff;
  border-radius: 5px;
}

.result h2 {
  margin: 0;
  padding: 0;
}

.result p {
  margin: 10px 0;
}

img {
  max-width: 100%;
}
</style>
