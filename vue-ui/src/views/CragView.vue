<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { getCrag, updateCrag, apiUrl } from "@/api/api";
import { useRoute } from "vue-router";

const route = useRoute();

const editingIndex = ref(null);
const image = ref("");
const cragData = ref({
  name: "",
  crags: [],
});

const svgWidth = ref(0);
const svgHeight = ref(0);
const draggingPointIndex = ref(null);

const savedCrags = ref([]);
const localCrags = ref([]);

const points = computed({
  get() {
    return localCrags.value[editingIndex.value]?.path ?? [];
  },
  set(newPoints) {
    if (editingIndex.value !== null) {
      localCrags.value[editingIndex.value].path = newPoints;
    }
  },
});

const editedLinePath = computed(() => {
  return `M ${points.value.map((point) => point.join(" ")).join(" L ")}`;
});

const notEditedlocalCragPaths = computed(() => {
  return localCrags.value
    .filter((crag, index) => index !== editingIndex.value)
    .map((crag) => {
      return `M ${crag.path.map((point) => point.join(" ")).join(" L ")}`;
    });
});

onMounted(async () => {
  const crag = await getCrag(`${route.params.region}/${route.params.crag}`);
  image.value = crag.image;
  cragData.value = { ...cragData.value, ...crag.data };
  savedCrags.value = crag.data?.crags ?? [];
  localCrags.value = [...savedCrags.value];

  const img = new Image();
  img.src = `${apiUrl}/${image.value}`;
  img.onload = () => {
    svgWidth.value = img.width;
    svgHeight.value = img.height;
  };
});

const addLocalCrag = () => {
  localCrags.value = [
    ...localCrags.value,
    {
      name: `Crag ${localCrags.value.length + 1}`,
      path: [],
    },
  ];
  editingIndex.value = localCrags.value.length - 1;
};

const handleSvgClick = (event: MouseEvent) => {
  if (editingIndex.value === null) {
    addLocalCrag();
  }
  const svg = event.target as SVGSVGElement;
  const pt = svg.createSVGPoint();
  pt.x = event.clientX;
  pt.y = event.clientY;
  const cursorpt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
  points.value = [...points.value, [cursorpt.x, cursorpt.y]];
};

const handleMouseDown = (index: number) => {
  draggingPointIndex.value = index;
};

const saveCrag = (index: number) => {
  editingIndex.value = null;
};

const handleMouseMove = (event: MouseEvent) => {
  if (draggingPointIndex.value !== null) {
    const svg = event.target as SVGSVGElement;
    const pt = svg.createSVGPoint();
    pt.x = event.clientX;
    pt.y = event.clientY;
    const cursorpt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
    points.value[draggingPointIndex.value] = [cursorpt.x, cursorpt.y];
  }
};

const handleMouseUp = () => {
  draggingPointIndex.value = null;
};

const uploadCrags = async () => {
  await updateCrag(`${route.params.region}/${route.params.crag}`, {
    crags: localCrags.value,
  });
};
</script>

<template>
  <div>
    <h1>Crag</h1>
    <div style="display: flex">
      <div class="image-container" style="flex: 1">
        <div class="image-wrapper">
          <img :src="`${apiUrl}/${image}`" />
          <svg
            :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
            preserveAspectRatio="xMidYMid meet"
            @click="handleSvgClick"
            @mousemove="handleMouseMove"
            @mouseup="handleMouseUp"
            class="overlay-svg"
          >
            <template v-if="editedLinePath">
              <circle
                v-for="(point, index) in points"
                :key="index"
                :cx="point[0]"
                :cy="point[1]"
                r="15"
                fill="red"
                @mousedown="handleMouseDown(index)"
              />
            </template>
            <path
              :d="editedLinePath"
              stroke="red"
              stroke-width="2"
              fill="none"
            />
            <path
              v-for="(path, index) in notEditedlocalCragPaths"
              :key="index"
              :d="path"
              stroke="blue"
              stroke-width="2"
              fill="none"
            />
          </svg>
        </div>
      </div>
      <div style="flex: 1; padding-left: 20px">
        <h2>Name: {{ cragData.name }}</h2>
        <p>Crags</p>
        <ul>
          <li v-for="(crag, index) in localCrags" :key="index">
            <input v-if="editingIndex === index" v-model="crag.name" />
            <span v-else>{{ crag.name }}</span>
            <button v-if="editingIndex === index" @click="saveCrag(index)">
              Save
            </button>
            <template v-else>
              <button @click="editingIndex = index">Edit</button>
              <button @click="localCrags.splice(index, 1)">Delete</button>
            </template>
          </li>
        </ul>
        <button @click="uploadCrags">Upload</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.image-container {
  position: relative;
  display: inline-block;
  max-width: 300px;
}

.image-wrapper {
  position: relative;
  width: 100%;
}

img {
  width: 100%;
  display: block;
}

.overlay-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: all;
}
</style>
