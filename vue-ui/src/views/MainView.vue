<script setup lang="ts">
import { ref, nextTick, computed, onMounted } from "vue";
import { findMatchingMatrix, apiUrl } from "@/api/api";

const getCoordinates = async function (): Promise<{
  latitude: number;
  longitude: number;
}> {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      console.log("Geolocation is supported by this browser.");
      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log("Latitude: " + position.coords.latitude);
          console.log("Longitude: " + position.coords.longitude);
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.error("Error getting coordinates: ", error);
          reject(error);
        }
      );
    } else {
      console.error("Geolocation is not supported by this browser.");
      reject("Geolocation is not supported by this browser.");
    }
  });
};

const availableLocations = [
  {
    name: "szczytna_widokowa",
    label: "Szczytna Widokowa",
    coordinates: {
      latitude: 50.411051,
      longitude: 16.456668,
    },
  },
  {
    name: "stokowka",
    label: "Stokowka",
    coordinates: {
      latitude: 50.8325,
      longitude: 20.4244,
    },
  },
];

// Function to calculate the distance using Haversine formula
function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of the Earth in kilometers
  const toRad = Math.PI / 180; // Conversion factor from degrees to radians

  // Convert degrees to radians
  lat1 = lat1 * toRad;
  lon1 = lon1 * toRad;
  lat2 = lat2 * toRad;
  lon2 = lon2 * toRad;

  // Differences in coordinates
  const dLat = lat2 - lat1;
  const dLon = lon2 - lon1;

  // Haversine formula
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  // Distance in kilometers
  const distance = R * c;

  return distance; // Returns the distance in kilometers
}

const distancesFromLocations = computed(() =>
  availableLocations
    .map((location) => {
      const distance = haversineDistance(
        coordinates.value.latitude,
        coordinates.value.longitude,
        location.coordinates.latitude,
        location.coordinates.longitude
      );
      return {
        name: location.name,
        label: location.label,
        distance,
      };
    })
    .sort((a, b) => a.distance - b.distance)
);

const coordinates = ref({ latitude: 0, longitude: 0 });
// TODO check if this needs to be on mounted
onMounted(async () => {
  try {
    coordinates.value = await getCoordinates();
  } catch (error) {
    console.error("Error getting coordinates: ", error);
  }
});

const matchingMatrixResult = ref(null);
const errorMessage = ref("");
const image1 = ref(null);
const image2 = ref(null);
const file1 = ref<File | null>(null);
const selectedFolder = ref("");
const image1Url = ref("");
const isMobile = ref(false);
const showImage1 = ref(true); // Ref to toggle images in mobile view
const showImage2 = computed(() => !isMobile.value || !showImage1.value);

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
  } catch (error) {
    errorMessage.value =
      "An error occurred while uploading the file and folder.";
    console.error(error);
  }
};

const svgWidth = computed(() => {
  if (!matchingMatrixResult.value?.image1?.width) return 0;
  return isMobile.value
    ? matchingMatrixResult.value.image1.width
    : matchingMatrixResult.value.image1.width +
        matchingMatrixResult.value.image2.width;
});

const firstImageWidthPercentage = computed(() => {
  if (!matchingMatrixResult.value?.image1?.width) return 0;
  return (matchingMatrixResult.value.image1.width / svgWidth.value) * 100;
});

const secondImageWidthPercentage = computed(() => {
  if (!matchingMatrixResult.value?.image2?.width) return 0;
  return (matchingMatrixResult.value.image2.width / svgWidth.value) * 100;
});

const svgHeight = computed(() => {
  if (!matchingMatrixResult.value) return 0;
  if (showImage1.value && showImage2.value)
    return Math.max(
      matchingMatrixResult.value.image1.height,
      matchingMatrixResult.value.image2.height
    );
  if (showImage1.value) return matchingMatrixResult.value.image1.height;
  if (showImage2.value) return matchingMatrixResult.value.image2.height;
  return 0;
});

const lines = computed(() => {
  if (!matchingMatrixResult.value) return [];
  return matchingMatrixResult.value.matched_points.map((match) => {
    const { point1, point2 } = match;
    return {
      x1: point1.x,
      y1: point1.y,
      x2: point2.x,
      y2: point2.y,
      show: ref(false),
      hovered: ref(false),
    };
  });
});

const pickedLines = computed(() =>
  lines.value.filter((line) => line.show.value)
);

const hoveredLines = computed(() =>
  lines.value.filter((line) => line.hovered.value)
);

const shownLines = computed(() => pickedLines.value.concat(hoveredLines.value));

const circleClicked = (line) => {
  console.log("circle clicked", line);
  line.show.value = !line.show.value;
};

const clearLines = () => {
  shownLines.value.forEach((line) => {
    line.show.value = false;
  });
};

const swapImage = () => {
  showImage1.value = !showImage1.value;
};

const pickLocation = (locationName) => {
  selectedFolder.value = locationName;
};

const crags = computed(() => {
  return matchingMatrixResult.value?.best_match_json_content?.crags || [];
});
</script>

<template>
  <div class="matching-matrix">
    <h1>Find Match</h1>
    <div>
      <small>Latitude: {{ coordinates.latitude }}</small>
      <br />
      <small>Longitude: {{ coordinates.longitude }}</small>
    </div>
    <!-- distances from locations -->
    <div>
      <h2>Distances from locations</h2>
      <ul>
        <li v-for="distance in distancesFromLocations" :key="distance.name">
          {{ distance.label }}: {{ distance.distance.toFixed(2) }} km
          <a href="#" @click.prevent="pickLocation(distance.name)"
            >Pick this location</a
          >
        </li>
      </ul>
    </div>
    <div v-if="errorMessage">{{ errorMessage }}</div>
    <div class="file-inputs">
      <input type="file" @change="handleFileChange1" />
      <select v-model="selectedFolder">
        <option disabled value="">Select Region</option>
        <option
          v-for="location in availableLocations"
          :key="location.name"
          :value="location.name"
        >
          {{ location.label }}
        </option>
      </select>
      <button @click="uploadFileAndFolder">Submit</button>
    </div>
    <div
      class="images-container"
      :style="{
        width: `${svgWidth}px`,
        maxWidth: `min(100%, ${svgWidth}px)`,
      }"
    >
      <img
        v-if="image1Url && (!isMobile || showImage1)"
        ref="image1"
        :width="`${firstImageWidthPercentage}%`"
        :src="image1Url"
        alt="image 1"
      />
      <img
        v-if="matchingMatrixResult?.image2 && showImage2"
        ref="image2"
        :width="`${secondImageWidthPercentage}%`"
        :src="`${apiUrl}/${matchingMatrixResult.image2.path}`"
        alt="image 2"
      />
      <div class="svg-wrapper">
        <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`">
          <template v-if="svgWidth && svgHeight">
            <template v-for="(line, index) in lines" :key="`circle-${index}`">
              <circle
                v-if="!isMobile || showImage1"
                :cx="line.x1"
                :cy="line.y1"
                :r="line.show.value ? 9 : 6"
                :stroke="line.show.value ? 'green' : 'black'"
                stroke-width="2"
                :fill="line.show.value ? 'green' : 'white'"
                :fill-opacity="line.show.value ? 1 : 0.5"
                @click="circleClicked(line)"
                @mouseover="line.hovered.value = true"
                @mouseleave="line.hovered.value = false"
                :class="{ shown: line.show.value }"
              />
              <circle
                v-if="!isMobile || !showImage1"
                :cx="
                  showImage1
                    ? line.x2 + matchingMatrixResult.image1.width
                    : line.x2
                "
                :cy="line.y2"
                :r="line.show.value ? 9 : 6"
                :stroke="line.show.value ? 'green' : 'black'"
                stroke-width="2"
                :fill="line.show.value ? 'green' : 'white'"
                :fill-opacity="line.show.value ? 1 : 0.5"
                @click="circleClicked(line)"
                @mouseover="line.hovered.value = true"
                @mouseleave="line.hovered.value = false"
                :class="{ shown: line.show.value }"
              />
            </template>
            <template v-if="!isMobile">
              <line
                v-for="(line, index) in shownLines"
                :key="`line-${index}`"
                :x1="line.x1"
                :y1="line.y1"
                :x2="line.x2 + matchingMatrixResult.image1.width"
                :y2="line.y2"
                stroke="green"
                stroke-width="3"
                @mouseover="line.hovered.value = true"
                @mouseleave="line.hovered.value = false"
              />
            </template>
          </template>
        </svg>
      </div>
    </div>
    <button
      @click="clearLines"
      :disabled="!pickedLines.length"
      style="margin-top: 20px"
    >
      Clear {{ isMobile ? "Dots" : "Lines" }}
    </button>
    <button
      v-if="isMobile"
      @click="swapImage"
      style="margin-top: 20px; margin-left: 10px"
      :disabled="!matchingMatrixResult"
    >
      Swap Image
    </button>
    <button
      @click="isMobile = !isMobile"
      style="margin-top: 20px; margin-left: 10px"
      :disabled="!matchingMatrixResult"
    >
      Toggle View
    </button>
    <div v-if="crags.length">
      <h2>Crags</h2>
      <ol :start="crags[0].line ?? 0">
        <li v-for="crag in crags" :key="crag.line">
          {{ crag.name }} (Grade: {{ crag.grade }}, Express Count:
          {{ crag.expressCount }})
        </li>
      </ol>
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

.images-container img {
  height: fit-content;
}

.svg-wrapper {
  position: absolute;
  height: auto;
  width: 100%;
}

.svg-wrapper svg {
  width: 100%;
}

pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

circle:hover {
  cursor: pointer;
}

circle {
  opacity: 0.8;
}

circle.shown {
  opacity: 1;
}
</style>
