<template>
  <div class="container"> 
    <ImageSliderCompare
    :srcLeft="'./public/portrait-265/left.png'"
    :srcRight="'./public/portrait-265/right.png'"
    />
  </div>
</template>

<script setup>
import ImageSliderCompare from 'vue3-image-compare-slider'
</script>

<style lang="scss" scoped>
  .container {
    width: 100%;
    height: 100%;
    background-color: #ccc;
  }
</style>
