<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import axios from "axios";

const apiUrl = import.meta.env.VITE_API_BASE_URL;

const file1 = ref<File | null>(null);
const file2 = ref<File | null>(null);
const image1Url = ref("");
const image2Url = ref("");
const matchingResult = ref(null);
const errorMessage = ref("");
const loading = ref(false);

const clickedPoints = ref([]);
const image1 = ref(null);
const image2 = ref(null);
const svgWidth = ref(0);
const svgHeight = ref(0);

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

  try {
    loading.value = true;
    await new Promise((resolve, reject) => {
      const reader1 = new FileReader();
      const reader2 = new FileReader();

      reader1.onload = async (e1) => {
        const img1 = new Image();
        img1.src = e1.target?.result as string;
        img1.onload = async () => {
          const src1 = cv.imread(img1);
          const maxDim1 = 840;
          const scale1 = maxDim1 / Math.max(src1.rows, src1.cols);
          const dsize1 = new cv.Size(src1.cols * scale1, src1.rows * scale1);
          const dst1 = new cv.Mat();
          cv.resize(src1, dst1, dsize1, 0, 0, cv.INTER_AREA);

          const canvas1 = document.createElement("canvas");
          cv.imshow(canvas1, dst1);
          const dataUrl1 = canvas1.toDataURL("image/jpeg");
          const resizedImgData1 = dataUrl1.split(",")[1];

          reader2.onload = async (e2) => {
            const img2 = new Image();
            img2.src = e2.target?.result as string;
            img2.onload = async () => {
              const src2 = cv.imread(img2);
              const maxDim2 = 840;
              const scale2 = maxDim2 / Math.max(src2.rows, src2.cols);
              const dsize2 = new cv.Size(
                src2.cols * scale2,
                src2.rows * scale2
              );
              const dst2 = new cv.Mat();
              cv.resize(src2, dst2, dsize2, 0, 0, cv.INTER_AREA);

              const canvas2 = document.createElement("canvas");
              cv.imshow(canvas2, dst2);
              const dataUrl2 = canvas2.toDataURL("image/jpeg");
              const resizedImgData2 = dataUrl2.split(",")[1];

              try {
                const response = await axios.post(`${apiUrl}/get_matching`, {
                  image1: resizedImgData1,
                  image2: resizedImgData2,
                });
                matchingResult.value = response.data;
                errorMessage.value = "";
                await nextTick();
                updateSvgDimensions();
              } catch (error) {
                errorMessage.value =
                  "An error occurred while uploading the files.";
                console.error(error);
              } finally {
                src1.delete();
                dst1.delete();
                src2.delete();
                dst2.delete();
                resolve(void 0);
              }
            };
          };
          reader2.onerror = (e) => {
            console.error("Error reading file: ", e);
            reject(e);
          };
          reader2.readAsDataURL(file2.value);
        };
      };
      reader1.onerror = (e) => {
        console.error("Error reading file: ", e);
        reject(e);
      };
      reader1.readAsDataURL(file1.value);
    });
  } catch (error) {
    errorMessage.value = "An error occurred while uploading the files.";
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const updateSvgDimensions = () => {
  if (image1.value && image2.value) {
    svgWidth.value = image1.value.width + image2.value.width;
    svgHeight.value = Math.max(image1.value.height, image2.value.height);
  }
};

const collectCoordinates = (event: MouseEvent) => {
  const svg = event.target as SVGSVGElement;
  const pt = svg.createSVGPoint();
  pt.x = event.clientX;
  pt.y = event.clientY;
  const cursorpt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
  clickedPoints.value.push([cursorpt.x, cursorpt.y]);
};

const clickedPointsOnImageOne = computed(() =>
  clickedPoints.value.filter(
    (point) => point[0] < matchingResult.value.image1.width
  )
);

const clickedPointsOnImageTwo = computed(() =>
  clickedPoints.value.filter(
    (point) => point[0] >= matchingResult.value.image1.width
  )
);

const clickedPointsOnImageTwoAbsolute = computed(() =>
  clickedPointsOnImageTwo.value.map((point) => [
    point[0] - matchingResult.value.image1.width,
    point[1],
  ])
);

const getMatch = (point, { inverse = false } = {}) => {
  const pointMat = cv.matFromArray(1, 1, cv.CV_32FC2, point);
  const match = new cv.Mat();
  cv.perspectiveTransform(pointMat, match, inverse ? hInverse.value : h.value);
  pointMat.delete();
  return [match.data32F[0], match.data32F[1]];
};

const correspondingOnImageTwo = computed(() => {
  const matches = clickedPointsOnImageOne.value.map((point) => getMatch(point));
  return matches;
});

const correspondingOnImageOne = computed(() => {
  const matches = clickedPointsOnImageTwoAbsolute.value.map((point) =>
    getMatch(point, { inverse: true })
  );
  return matches;
});

const h = computed(() => {
  if (!matchingResult.value?.homography_matrix) return null;
  const { homography_matrix } = matchingResult.value;
  return cv.matFromArray(3, 3, cv.CV_32F, homography_matrix);
});

const hInverse = computed(() => {
  if (!matchingResult.value?.homography_matrix_inverse) return null;
  const { homography_matrix_inverse } = matchingResult.value;
  return cv.matFromArray(3, 3, cv.CV_32F, homography_matrix_inverse);
});

const firstImageWidthPercentage = computed(() => {
  if (!matchingResult.value?.image1?.width) return 0;
  return (matchingResult.value.image1.width / svgWidth.value) * 100;
});

const secondImageWidthPercentage = computed(() => {
  if (!matchingResult.value?.image2?.width) return 0;
  return (matchingResult.value.image2.width / svgWidth.value) * 100;
});
</script>

<template>
  <div class="match-images">
    <h1>Match Images</h1>
    <div v-if="errorMessage">{{ errorMessage }}</div>
    <div class="file-inputs">
      <input type="file" @change="handleFileChange1" />
      <input type="file" @change="handleFileChange2" />
      <button @click="uploadFiles" :disabled="loading">
        Submit
        <div v-if="loading" class="spinner"></div>
      </button>
    </div>
    <div class="images-container">
      <img
        v-if="image1Url"
        ref="image1"
        :width="`${firstImageWidthPercentage}%`"
        :src="image1Url"
        alt="Image 1"
      />
      <img
        v-if="image2Url"
        ref="image2"
        :width="`${secondImageWidthPercentage}%`"
        :src="image2Url"
        alt="Image 2"
      />
      <div class="svg-wrapper" @click="collectCoordinates">
        <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`">
          <template v-if="svgWidth && svgHeight">
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
              :cx="point[0] + matchingResult.image1.width"
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
          </template>
        </svg>
      </div>
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
  position: relative;
  display: flex;
}

.svg-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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

.spinner {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-left-color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
