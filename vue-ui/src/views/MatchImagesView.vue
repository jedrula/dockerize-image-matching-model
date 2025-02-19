<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";

const apiUrl = import.meta.env.VITE_API_BASE_URL;

const file1 = ref<File | null>(null);
const file2 = ref<File | null>(null);
const image1Url = ref("");
const image2Url = ref("");
const matchingResult = ref(null);
const errorMessage = ref("");

const handleFileChange1 = (event: Event) => {
  const fileInput = event.target as HTMLInputElement;
  file1.value = fileInput.files?.[0] || null;
  if (file1.value) {
    image1Url.value = URL.createObjectURL(file1.value);
  }
};

const handleFileChange2 = (event: Event) => {
  const fileInput = event.target as HTMLInputElement;
  file2.value = fileInput.files?.[0] || null;
  if (file2.value) {
    image2Url.value = URL.createObjectURL(file2.value);
  }
};

const uploadFiles = async () => {
  if (!file1.value || !file2.value) {
    errorMessage.value = "Please select both files.";
    return;
  }

  const formData = new FormData();
  formData.append("image1", file1.value);
  formData.append("image2", file2.value);

  try {
    const response = await axios.post(`${apiUrl}/get_matching`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    matchingResult.value = response.data;
    errorMessage.value = "";
  } catch (error) {
    errorMessage.value = "An error occurred while uploading the files.";
    console.error(error);
  }
};
</script>

<template>
  <div class="match-images">
    <h1>Match Images</h1>
    <div v-if="errorMessage">{{ errorMessage }}</div>
    <div class="file-inputs">
      <input type="file" @change="handleFileChange1" />
      <input type="file" @change="handleFileChange2" />
      <button @click="uploadFiles">Submit</button>
    </div>
    <div class="images-container">
      <img v-if="image1Url" :src="image1Url" alt="Image 1" />
      <img v-if="image2Url" :src="image2Url" alt="Image 2" />
    </div>
    <div v-if="matchingResult">
      <h2>Matching Result</h2>
      <pre>{{ JSON.stringify(matchingResult, null, 2) }}</pre>
    </div>
  </div>
</template>

<style scoped>
.match-images {
  padding: 20px;
  background-color: #fff;
  border-radius: 5px;
}

.file-inputs {
  margin-bottom: 20px;
}

.images-container {
  display: flex;
  gap: 10px;
}

img {
  max-width: 100%;
  height: auto;
}

pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}
</style>
