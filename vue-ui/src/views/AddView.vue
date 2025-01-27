<script setup lang="ts">
import { ref, computed } from "vue";
import { apiUrl } from "@/api/api";
</script>

<template>
  <div>
    <h1>Add Topo</h1>
    <input type="file" @change="onFileChange" />
    <button @click="onUpload">Upload</button>
  </div>
</template>
