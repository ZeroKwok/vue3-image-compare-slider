<template>
  <div class="container">
    <div class="image-viewer">
      <ImageSliderCompare ref="imageView" :srcLeft="currentLeft" :srcRight="currentRight" v-model:zoom="zoom" :fit="fitMode" />

      <div class="controls">
        <el-slider class="zoom" v-model="zoom" :min="10" :max="400" :step="10" :vertical="true" height="80px"
          :format-tooltip="val => `Zoom: ${val}%`" />

        <el-dropdown class="fit-mode" @command="mode => imageView.setFitMode(mode)">
          <el-button plain>
            <el-icon><FullScreen /></el-icon>
          </el-button>
    
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="1:1">1:1</el-dropdown-item>
              <el-dropdown-item command="scale-down">自适应</el-dropdown-item>
              <el-dropdown-item command="contain">自适应窗口</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

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

const imageView = ref(null);
const fitMode = ref('contain');
const zoom = ref(100);

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
    position: relative;

    .controls {
      position: absolute;
      width: 50px;
      right: 10px;

      top: 50%;
      transform: translate(0, -50%);

      display: flex;
      flex-direction: column;
      padding: 0.5rem;
      gap: 1rem;

      border-radius: 4px;
      border: 1px solid #999;
      box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
      transition: all 0.2s ease;
      user-select: none;

      &:hover,
      &:active {
        background: #ffff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
      }

      .zoom {
        :deep(.el-slider__runway) {
          background-color: #ddd;
          width: 4px;
          flex-shrink: 0;
          flex-basis: 4px; 
          border: 1px solid #0005
        }

        :deep(.el-slider__bar) {
          background-color: #fff;
          width: 2px;
          border-radius: 2px;
        }

        :deep(.el-slider__button) {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #ffff;
          border: 1px solid #0005 !important;
          transform: translateX(-25%);
        }
      }

      .fit-mode {
        button {
          padding: 0.5rem;
          color: rgba(0, 0, 0, 0.8);
          border-color: rgba(0, 0, 0, 0.8);

          &:focus-visible {
            outline: 2px solid #000;
          }
        }
      }
    }
  }

  .image-list {
    border: 1px solid #ccc;
    padding: 3px 3px;
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
        box-shadow: 0 0 0 2px #000;
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