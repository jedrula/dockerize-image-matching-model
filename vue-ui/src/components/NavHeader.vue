<template>
  <nav>
    <router-link to="/">Home</router-link>
    <router-link to="/add-region">Add Region</router-link>
    <router-link to="/regions">Regions</router-link>
    <router-link to="/match-images">Match Images</router-link>
    <router-link to="/matching_matrix">Matching Matrix</router-link>
  </nav>
</template>

<script lang="ts">
export default {};
</script>

<style scoped>
nav {
  display: flex;
  gap: 1rem;
}
</style>
