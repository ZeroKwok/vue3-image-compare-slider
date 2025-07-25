<template>
  <div class="image-compare-slider">
    <div class="container" ref="containerRef" @mousedown.prevent @wheel.prevent="handleWheel">
      <img :src="srcLeft" class="image left" alt="Left" ref="leftRef" @load="handleImageLoad"
        @mousedown.passive="startDrag" @touchstart.passive="startDrag">
      <img :src="srcRight" class="image right" alt="Right" ref="rightRef" @load="handleImageLoad"
        @mousedown.passive="startDrag" @touchstart.passive="startDrag">

      <div class="slider" ref="sliderRef" :style="{ left: `${sliderPosition}px` }" 
        @mousedown.passive="(e)=>startDrag(e, true)" @touchstart.passive="(e)=>startDrag(e, true)">
        <img class="button" src="../assets/icon_button_slider.svg" alt="Slider handle">
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue';

const props = defineProps({
  srcLeft: {
    type: String,
    required: true
  },
  srcRight: {
    type: String,
    required: true
  },
  zoom: {
    type: Number,
    default: 100
  }
});

const emit = defineEmits(['update:zoom'])

const containerRef = ref(null);
const sliderRef = ref(null);
const leftRef = ref(null);
const rightRef = ref(null);

const sliderPosition = ref(0);
const sliderRatio = ref(0);
const sliderOffsetX = ref(0);

const moveOffsetX = ref(0);
const moveOffsetY = ref(0);

const isDragging = ref(false);
const isSliderDragging = ref(false);

const zoomVal = ref(props.zoom);
const zoomMax = ref(400);
const zoomMin = ref(10);
const zoomStep = ref(10);

const clamp = (value, min, max) => {
  return Math.max(min, Math.min(max, value));
};

const handleWheel = (e) => {
  zoomVal.value = clamp(zoomVal.value + (e.deltaY < 0 ? zoomStep.value  : -zoomStep.value ), zoomMin.value , zoomMax.value );
};

watch(zoomVal, (newZoom) => {
  emit('update:zoom', newZoom);
  updateImageScale(newZoom/100);
  updateSliderPositionByRatio(sliderRatio.value);
});

watch(() => props.zoom, (newVal) => {
  zoomVal.value = newVal;
});

const getPos = (e) => { 
  let x, y;
  if (e.type === 'touchmove') {
    x = e.touches[0].clientX;
    y = e.touches[0].clientY;
  } else {
    x = e.clientX;
    y = e.clientY;
  }
  return { x, y };
};

const startDrag = (e, isSlider = false) => {
  isDragging.value = true;
  isSliderDragging.value = isSlider;

  if (!isSlider) {
    initImagePositionOffset(e);
  }

  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('touchmove', handleDrag, { passive: false });
  document.addEventListener('mouseup', stopDrag);
  document.addEventListener('touchend', stopDrag);
};

const stopDrag = () => {
  isDragging.value = false;
  isSliderDragging.value = false;
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('touchmove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
  document.removeEventListener('touchend', stopDrag);
};

const handleDrag = (e) => {
  if (!isDragging.value || !containerRef.value)
    return;
  e.preventDefault();

  const { x, y } = getPos(e);
  const clientRect = containerRef.value.getBoundingClientRect()
  if (isSliderDragging.value) {
    updateSliderPosition(x - clientRect.left, clientRect);
  } else {
    updateImagePosition(x - clientRect.left, y - clientRect.top, clientRect);
  }
};

const updateSliderPosition = (x, rect) => { 
  const zoom = zoomVal.value / 100;
  const vW = rect.width;          // viewport width
  const iW = vW * zoom;           // image width
  const sX = clamp(x, 0, vW);     // slider x
  const sRatio = sX / vW;         // slider x ratio

  const offX = (iW - vW) / 2 - sliderOffsetX.value;
  const iX = (sX + offX) / zoom;  // slider x on image

  sliderRatio.value = sRatio;
  sliderPosition.value = sX;
  updateImageClipPath(iX);

  console.log(
    `update: x: ${x}, rect: ${rect.left}~${rect.right}:${vW}, zoom: ${zoom}, iW: ${iW}, ` +
    `sRatio: ${sRatio}, sX: ${sX}, iX: ${iX}, offX: ${offX}`);
};

const updateSliderPositionByRatio = (sRatio) => {
  const rect = containerRef.value.getBoundingClientRect();
  updateSliderPosition(rect.width * sRatio, rect);
};

const initImagePositionOffset = (e) => { 
    const { x, y } = getPos(e);
    const imgRect = leftRef.value.getBoundingClientRect();
    moveOffsetX.value =  x - imgRect.left;
    moveOffsetY.value =  y - imgRect.top;
};

const updateImagePosition = (x, y, rect) => {
  const imgRect = leftRef.value.getBoundingClientRect();
  const zoom = zoomVal.value / 100;
  const vW = rect.width;
  const iW = vW * zoom;
  const offX = (iW - vW) / 2;
  const iX = x - moveOffsetX.value + offX;
  const iY = y - moveOffsetY.value + imgRect.height / 2;

  sliderOffsetX.value = iX;
  updateImagePositionOffset(iX, iY);
  updateSliderPositionByRatio(sliderRatio.value);

  console.log(
    `update: pox: ${x},${y}, rect: ${rect.left}~${rect.right}:${rect.top}~${rect.bottom}, zoom: ${zoom}, vW: ${vW}, iW: ${iW}, ` +
    `ox: ${moveOffsetX.value}, oy: ${moveOffsetY.value}`);
}

const updateImageClipPath = (pos) => {
  leftRef.value.style.clipPath = `inset(0 calc(100% - ${pos}px) 0 0)`;
  rightRef.value.style.clipPath = `inset(0 0 0 ${pos}px)`;
};

const updateImageScale = (zoom) => {
  leftRef.value.style.transform = `translate(0, -50%) scale(${zoom})`;
  rightRef.value.style.transform = `translate(0, -50%) scale(${zoom})`;
};

const updateImagePositionOffset = (x, y) => {
  leftRef.value.style.left = `${x}px`;
  leftRef.value.style.top = `${y}px`;

  rightRef.value.style.left = leftRef.value.style.left;
  rightRef.value.style.top = leftRef.value.style.top;
};

const handleImageLoad = () => { 
  updateSliderPositionByRatio(0.5);
};

const handleResize = () => {
  if (!containerRef.value) return;
  updateSliderPositionByRatio(sliderRatio.value);
};

const setFitMode = (mode) => {
  console.log('setFitMode: ', mode);
  switch (mode) {
    case '1:1':
      break;

    case 'contain':
      break;

    case 'scale-down':
      break;
  }
};

defineExpose({
  setFitMode,
})

</script>

<style scoped lang="scss">
.image-compare-slider {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #fcfcfc;
  user-select: none;

  .container {
    display: flex;
    flex-direction: row;
    position: relative;
    height: 100%;
    overflow: hidden;;

    .image {
      position: absolute;
      top: 50%;
      left: 0;
      transform: translate(0, -50%);
      will-change: transform, clip-path;

      width: 100%;
      object-fit: contain;
      user-select: none;
      cursor: move;
    }

    .slider {
      position: absolute;
      top: 0;
      width: 4px;
      height: 100%;
      background-color: white;
      cursor: ew-resize;
      z-index: 10;
      touch-action: none;
      user-select: none;
      transform: translate(-2px, 0);

      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
  }
}
</style>