<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { findMatchingMatrix, apiUrl } from "@/api/api";
import Tooltip from "@/components/Tooltip.vue";

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

const collectCoordinates = (event: MouseEvent) => {
  // this function will alert coordinates of the clicked point relateive to the left top corner of the svg
  const svg = document.querySelector("svg");
  if (!svg) {
    console.error("SVG element not found.");
    return;
  }
  const pt = svg.createSVGPoint();
  pt.x = event.clientX;
  pt.y = event.clientY;
  const cursorpt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
  console.log("Coordinates2: ", cursorpt.x, cursorpt.y);
  clickedPoints.value.push([cursorpt.x, cursorpt.y]);
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

const h = computed(() => {
  if (!matchingMatrixResult.value?.homography_matrix) return null;
  const { homography_matrix } = matchingMatrixResult.value;
  return cv.matFromArray(3, 3, cv.CV_32F, homography_matrix);
});

const hInverse = computed(() => {
  if (!matchingMatrixResult.value?.homography_matrix_inverse) return null;
  const { homography_matrix_inverse } = matchingMatrixResult.value;
  return cv.matFromArray(3, 3, cv.CV_32F, homography_matrix_inverse);
});

function getMatch(point, { inverse = false } = {}) {
  const pointMat = cv.matFromArray(1, 1, cv.CV_32FC2, point);
  const match = new cv.Mat();
  cv.perspectiveTransform(pointMat, match, inverse ? hInverse.value : h.value);
  pointMat.delete();
  return [match.data32F[0], match.data32F[1]];
}

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
const hasCoordinates = computed(() => coordinates.value.latitude !== 0);
const clickedPoints = ref([]);
const clickedPointsOnImageOne = computed(() =>
  clickedPoints.value.filter(
    (point) => point[0] < matchingMatrixResult.value.image1.width
  )
);
const correspondingOnImageTwo = computed(() => {
  const matches = clickedPointsOnImageOne.value.map((point) => getMatch(point));
  return matches;
});
const clickedPointsOnImageTwo = computed(() =>
  clickedPoints.value.filter(
    (point) => point[0] >= matchingMatrixResult.value.image1.width
  )
);

const clickedPointsOnImageTwoAbsolute = computed(() =>
  clickedPointsOnImageTwo.value.map((point) => [
    point[0] - matchingMatrixResult.value.image1.width,
    point[1],
  ])
);

const correspondingOnImageOne = computed(() => {
  const matches = clickedPointsOnImageTwoAbsolute.value.map((point) =>
    getMatch(point, { inverse: true })
  );
  return matches;
});

// TODO check if this needs to be on mounted
onMounted(async () => {
  try {
    coordinates.value = await getCoordinates();
  } catch (error) {
    console.error("Error getting coordinates: ", error);
  }
});

const matchingMatrixResult = ref(null);
const loading = ref(false);
const errorMessage = ref("");
const image1 = ref(null);
const image2 = ref(null);
const file1 = ref<File | null>(null);
const selectedFolder = ref("");
const image1Url = ref("");
const isMobile = ref(true);
const showImage1 = ref(true); // Ref to toggle images in mobile view
const showImage2 = computed(() => !isMobile.value || !showImage1.value);
const showIdentifiedMatchingPoints = ref(false);
const showTooltip = ref(false);
const tooltipContent = ref("");
const tooltipX = ref(0);
const tooltipY = ref(0);

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
    loading.value = true;
    await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const img = new Image();
        img.src = e.target?.result as string;
        img.onload = async () => {
          try {
            const src = cv.imread(img);
            const maxDim = 840;
            const scale = maxDim / Math.max(src.rows, src.cols);
            const dsize = new cv.Size(src.cols * scale, src.rows * scale);
            const dst = new cv.Mat();
            cv.resize(src, dst, dsize, 0, 0, cv.INTER_AREA);

            console.log("dst", dst);
            // const resizedImgData = cv.imencode(".jpg", dst).toString("base64");

            // Convert the resized image to a base64 string using a canvas
            const canvas = document.createElement("canvas");
            cv.imshow(canvas, dst);
            const dataUrl = canvas.toDataURL("image/jpeg");
            // consider also converting to grayscale here, maybe could save some bandwith on that
            const resizedImgData = dataUrl.split(",")[1];

            const response = await findMatchingMatrix(
              resizedImgData,
              selectedFolder.value,
              (progressEvent) => {
                console.log(
                  "Upload progress:",
                  progressEvent.loaded / progressEvent.total
                );
              }
            );

            matchingMatrixResult.value = response;
            src.delete();
            dst.delete();
            resolve(void 0);
          } catch (error) {
            console.error("Error processing image: ", error);
            reject(error);
          }
        };
      };
      reader.onerror = (e) => {
        console.error("Error reading file: ", e);
        reject(e);
      };
      reader.readAsDataURL(file1.value);
    });
  } catch (error) {
    errorMessage.value =
      "An error occurred while uploading the file and folder.";
    console.error(error);
  } finally {
    loading.value = false;
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

const crags = computed(() => {
  return matchingMatrixResult.value?.best_match_json_content?.crags || [];
});

const cragsPathsOnImageOne = computed(() => {
  return crags.value.map((crag) => {
    const points = crag.path ?? [];
    return points.map((point) => {
      return getMatch(point, { inverse: true });
    });
  });
});

const showCragTooltip = (event, crag) => {
  console.log("showCragTooltip", event, crag);
  tooltipContent.value = `
    Name: ${crag.name} <br>
    Grade: ${crag.grade} <br>
    Express Count: ${crag.expressCount} <br>
  `;
  tooltipX.value = event.clientX + 10;
  tooltipY.value = event.clientY + 10;
  showTooltip.value = true;
};

const hideCragTooltip = () => {
  showTooltip.value = false;
};
</script>

<template>
  <div class="matching-matrix">
    <div style="position: fixed; top: 0; right: 0; padding: 10px">
      <small
        >{{ coordinates.latitude.toFixed(2) }}
        {{ coordinates.longitude.toFixed(2) }}</small
      >
    </div>
    <div v-if="errorMessage">{{ errorMessage }}</div>
    <div v-if="!matchingMatrixResult" class="matching-form">
      <input type="file" @change="handleFileChange1" />
      <div style="display: flex; align-items: center; gap: 5px">
        <select v-model="selectedFolder">
          <option disabled value="">Select Region</option>
          <option
            v-for="location in distancesFromLocations.length
              ? distancesFromLocations
              : availableLocations"
            :key="location.name"
            :value="location.name"
          >
            {{ location.label }}
            {{ hasCoordinates ? `(${location.distance.toFixed(2)} km)` : "" }}
          </option>
        </select>
        <div v-if="!selectedFolder && hasCoordinates">
          <small>
            <a
              href="#"
              @click.prevent="selectedFolder = distancesFromLocations[0].name"
            >
              Use closest location: {{ distancesFromLocations[0].label }}
            </a>
          </small>
        </div>
      </div>
      <button @click="uploadFileAndFolder">Submit</button>
    </div>
    <div v-if="loading" class="spinner" style="margin: 10px auto" />
    <div v-if="matchingMatrixResult">
      <h2 v-if="matchingMatrixResult?.best_match_json_content.name">
        {{ matchingMatrixResult.best_match_json_content.name }}
      </h2>
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
        <div class="svg-wrapper" @click="collectCoordinates">
          <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`">
            <template v-if="svgWidth && svgHeight">
              <template
                v-for="(path, index) in cragsPathsOnImageOne"
                :key="index"
              >
                <!-- Invisible wider path for better hover detection -->
                <path
                  class="hover-path"
                  :d="`M ${path.map((point) => point.join(',')).join(' L ')}`"
                  fill="none"
                  stroke="transparent"
                  stroke-width="20"
                  @mouseover="showCragTooltip($event, crags[index])"
                  @mouseleave="hideCragTooltip"
                />
                <!-- Visible thin line -->
                <path
                  class="e"
                  :d="`M ${path.map((point) => point.join(',')).join(' L ')}`"
                  fill="none"
                  :stroke="`hsl(${
                    (index * 360) / cragsPathsOnImageOne.length
                  }, 100%, 50%)`"
                  stroke-width="2"
                />
              </template>
              <circle
                v-for="clickedPoint in clickedPointsOnImageOne"
                :key="clickedPoint"
                :cx="clickedPoint[0]"
                :cy="clickedPoint[1]"
                r="5"
                fill="red"
              />
              <circle
                v-for="(point, index) in correspondingOnImageTwo"
                :key="index"
                :cx="
                  point[0] +
                  (showImage1 ? matchingMatrixResult.image1.width : 0)
                "
                :cy="point[1]"
                r="5"
                fill="blue"
              />
              <circle
                v-for="clickedPoint in clickedPointsOnImageTwo"
                :key="clickedPoint"
                :cx="clickedPoint[0]"
                :cy="clickedPoint[1]"
                r="5"
                fill="yellow"
              />
              <circle
                v-for="(point, index) in correspondingOnImageOne"
                :key="index"
                :cx="point[0]"
                :cy="point[1]"
                r="5"
                fill="pink"
              />
              <template v-if="showIdentifiedMatchingPoints">
                <template
                  v-for="(line, index) in lines"
                  :key="`circle-${index}`"
                >
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
        @click="showIdentifiedMatchingPoints = !showIdentifiedMatchingPoints"
        style="margin-top: 20px"
      >
        Toggle Matching Points
      </button>
      <button
        @click="clearLines"
        :disabled="!pickedLines.length"
        style="margin-top: 20px; margin-left: 10px"
      >
        Clear {{ isMobile ? "Dots" : "Lines" }}
      </button>
      <!-- Clear Custom -->
      <button
        @click="clickedPoints = []"
        :disabled="!clickedPoints.length"
        style="margin-top: 20px; margin-left: 10px"
      >
        Clear Custom
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
      <pre>
        {{ clickedPointsOnImageTwoAbsolute }}
      </pre>
      {{ tooltipX }}
      <Tooltip v-show="showTooltip" :x="tooltipX" :y="tooltipY">
        <div v-html="tooltipContent"></div>
      </Tooltip>
      <div v-if="crags.length">
        <h2>Crags</h2>
        <ol :start="crags[0].line ?? 0">
          <li v-for="crag in crags" :key="crag.line">
            {{ crag.name }} (Grade: {{ crag.grade }}, Express Count:
            {{ crag.expressCount }})
          </li>
        </ol>
      </div>
      <a
        href="#"
        @click="matchingMatrixResult = null"
        style="display: block; text-align: center; color: red; margin-top: 10px"
        >Start Over</a
      >
    </div>
  </div>
</template>

<style scoped>
.matching-matrix {
  background-color: #fff;
  border-radius: 5px;
}

.matching-form {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  gap: 10px;
}

.images-container {
  position: relative;
  display: flex;
}

.images-container img {
  height: max-content;
  height: intrinsic;
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

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #000;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
