<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getRegion, addCrag, apiUrl } from "@/api/api";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const regionData = ref({});
const newCragName = ref("");
const newCragImage = ref<File | null>(null);
const newCragImageUrl = ref("");
const showAddCragForm = ref(false);
const errorMessage = ref("");

onMounted(async () => {
  const region = await getRegion(route.params.region);
  console.log(region);
  regionData.value = region;
});

const handleFileChange = (event: Event) => {
  const fileInput = event.target as HTMLInputElement;
  newCragImage.value = fileInput.files?.[0] || null;
  if (newCragImage.value) {
    newCragImageUrl.value = URL.createObjectURL(newCragImage.value);
  }
};

const onAddCrag = async () => {
  if (!newCragName.value || !newCragImage.value) {
    errorMessage.value = "Please provide both a name and an image.";
    return;
  }

  try {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const img = new Image();
      img.src = e.target?.result as string;
      img.onload = async () => {
        const src = cv.imread(img);
        const maxDim = 840;
        const scale = maxDim / Math.max(src.rows, src.cols);
        const dsize = new cv.Size(src.cols * scale, src.rows * scale);
        const dst = new cv.Mat();
        cv.resize(src, dst, dsize, 0, 0, cv.INTER_AREA);

        const canvas = document.createElement("canvas");
        cv.imshow(canvas, dst);
        const dataUrl = canvas.toDataURL("image/jpeg");
        const resizedImgData = dataUrl.split(",")[1];

        const cragData = {
          name: newCragName.value,
          image: resizedImgData,
        };

        await addCrag({
          region_name: route.params.region as string,
          ...cragData,
        });
        router.push(`/crag/${route.params.region}/${newCragName.value}`);
      };
    };
    reader.readAsDataURL(newCragImage.value);
  } catch (error) {
    errorMessage.value = "An error occurred while adding the crag.";
    console.error(error);
  }
};
</script>

<template>
  <div>
    <h1>Region {{ route.params.region }}</h1>
    <div
      v-for="{ name, path } in regionData"
      :key="path"
      @click="$router.push(`/crag/${route.params.region}/${name}`)"
    >
      <img :src="`${apiUrl}/${path}`" />
      <p>{{ name }}</p>
    </div>
    <button @click="showAddCragForm = true">Add New Crag</button>
    <div v-if="showAddCragForm">
      <h2>Add New Crag</h2>
      <input type="text" v-model="newCragName" placeholder="Enter crag name" />
      <input type="file" @change="handleFileChange" />
      <img v-if="newCragImageUrl" :src="newCragImageUrl" alt="New Crag Image" />
      <button @click="onAddCrag">Save</button>
      <button @click="showAddCragForm = false">Cancel</button>
      <div v-if="errorMessage">{{ errorMessage }}</div>
    </div>
  </div>
</template>

<style scoped>
img {
  width: 300px;
}

button {
  margin-top: 10px;
  padding: 10px 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

input[type="text"] {
  display: block;
  margin-bottom: 10px;
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
}

input[type="file"] {
  display: block;
  margin-bottom: 10px;
}

img[alt="New Crag Image"] {
  max-width: 100%;
  height: auto;
  margin-bottom: 10px;
}
</style>
