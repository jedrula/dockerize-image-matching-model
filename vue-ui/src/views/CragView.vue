<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { getCrag, apiUrl } from "@/api/api";
import { useRoute } from "vue-router";

const route = useRoute();

const image = ref("");
const cragData = ref({
  name: "",
  crags: [],
});

const svgWidth = ref(0);
const svgHeight = ref(0);
const points = ref([]);

const linePath = computed(() => {
  return `M ${points.value.map((point) => point.join(" ")).join(" L ")}`;
});

onMounted(async () => {
  const crag = await getCrag(`${route.params.region}/${route.params.crag}`);
  image.value = crag.image;
  cragData.value = { ...cragData.value, ...crag.data };

  const img = new Image();
  img.src = `${apiUrl}/${image.value}`;
  img.onload = () => {
    svgWidth.value = img.width;
    svgHeight.value = img.height;
  };
});

const handleSvgClick = (event: MouseEvent) => {
  const svg = event.target as SVGSVGElement;
  const pt = svg.createSVGPoint();
  pt.x = event.clientX;
  pt.y = event.clientY;
  const cursorpt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
  points.value = [...points.value, [cursorpt.x, cursorpt.y]];
};
</script>

<template>
  <div>
    <h1>Crag</h1>
    <div class="image-container">
      <img :src="`${apiUrl}/${image}`" />
      <svg
        :width="svgWidth"
        :height="svgHeight"
        @click="handleSvgClick"
        class="overlay-svg"
      >
        <path :d="linePath" stroke="red" stroke-width="2" fill="none" />
      </svg>
    </div>
    <h2>Name: {{ cragData.name }}</h2>
    <p>Crags: {{ cragData.crags }}</p>
  </div>
</template>

<style scoped>
.image-container {
  position: relative;
  display: inline-block;
}

img {
  width: 300px;
}

.overlay-svg {
  position: absolute;
  top: 0;
  left: 0;
}
</style>
