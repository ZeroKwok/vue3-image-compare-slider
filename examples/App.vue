<template>
  <div class="container">
    <div class="image-viewer">
      <ImageSliderCompare :srcLeft="currentLeft" :srcRight="currentRight" />
    </div>

    <div class="image-list">
      <div v-for="name in examples" :key="name" class="item" :class="{ active: name === currentName }"
        @click="currentName = name">
        <img :src="getItemImage(name, '2')" :alt="name" />
        <span class="name">{{ name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import ImageSliderCompare from "vue3-image-compare-slider";

const examples = [
  'portrait-265',
  'bit',
  'colour',
  'dark tone',
  'different',
  'bigger',
  'look like 1',
  'look like 2',
  'look like 3',
];
const currentName = ref(examples[0]);

const getItemImage = (name, label = '1') => `./public/${name}/${label}.jpg`;
const currentLeft = computed(() => getItemImage(currentName.value, '1'));
const currentRight = computed(() => getItemImage(currentName.value, '2'));
</script>

<style lang="scss" scoped>
.container {
  width: 100%;
  height: 100%;
  background-color: #fff;

  display: flex;
  flex-direction: column;
  padding: 1rem;
  gap: 1.5rem;

  .image-viewer {
    flex-grow: 1;
    border: 1px solid #ccc;
  }

  .image-list {
    border: 1px solid #ccc;
    padding: 3px 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 0.6rem;

    .item {
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      transition: all 0.2s ease;
      padding: 0.5rem;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
      }

      &.active {
        background-color: #e0f7fa;
        box-shadow: 0 0 0 2px #1f1f1f;
      }

      img {
        width: 100%;
        aspect-ratio: 1;
        object-fit: cover;
        border-radius: 4px;
      }

      .name {
        margin-top: 0.5rem;
        font-size: 0.8rem;
        color: #424242;
        text-align: center;
        word-break: break-word;
      }
    }
  }
}
</style>