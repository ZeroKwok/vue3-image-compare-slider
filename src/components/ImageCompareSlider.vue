<template>
  <div class="image-compare-slider">
    <div class="viewport" ref="viewportRef" @mousedown.prevent @wheel.prevent="handleWheel">
      <img :src="left" class="image left" alt="Left" ref="leftRef" @load="handleImageLoad(true)"
        @mousedown.passive="startDrag" @touchstart.passive="startDrag">
      <img :src="right" class="image right" alt="Right" ref="rightRef" @load="handleImageLoad(false)"
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
  left: {
    type: String,
    required: true
  },
  right: {
    type: String,
    required: true
  },
  zoom: {
    type: Number,
    default: 100
  },
  zoomRange: {
    type: Object,
    default: () => ({min: 10, max: 400, step: 10})
  },
});

const emit = defineEmits(['update:zoom'])

const viewportRef = ref(null);
const sliderRef = ref(null);
const leftRef = ref(null);
const rightRef = ref(null);
const imageSize = ref({width: 0, height: 0});

const sliderPosition = ref(0);
const sliderRatio = ref(0);
const sliderOffsetX = ref(0);

const clickOffsetX = ref(0);
const clickOffsetY = ref(0);

const isDragging = ref(false);
const isSliderDragging = ref(false);

const zoomVal  = ref(props.zoom);
const zoomMin  = ref(props.zoomRange.min);
const zoomMax  = ref(props.zoomRange.max);
const zoomStep = ref(props.zoomRange.step);

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
    leftRef.value.classList.add('draging');
    rightRef.value.classList.add('draging');
  }

  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('touchmove', handleDrag, { passive: false });
  document.addEventListener('mouseup', stopDrag);
  document.addEventListener('touchend', stopDrag);
};

const stopDrag = () => {
  isDragging.value = false;
  isSliderDragging.value = false;

  leftRef.value.classList.remove('draging');
  rightRef.value.classList.remove('draging');

  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('touchmove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
  document.removeEventListener('touchend', stopDrag);
};

const handleDrag = (e) => {
  if (!isDragging.value || !viewportRef.value)
    return;
  e.preventDefault();

  const { x, y } = getPos(e);
  const viewportRect = viewportRef.value.getBoundingClientRect()
  if (isSliderDragging.value) {
    updateSliderPosition(x - viewportRect.left, viewportRect);
  } else {
    updateImagePosition(x - viewportRect.left, y - viewportRect.top, viewportRect);
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
  const rect = viewportRef.value.getBoundingClientRect();
  updateSliderPosition(rect.width * sRatio, rect);
};

const initImagePositionOffset = (e) => { 
    const { x, y } = getPos(e);
    const imgRect = leftRef.value.getBoundingClientRect();

    // 计算点击位置相对于图片的左上角的偏移量
    clickOffsetX.value =  x - imgRect.left;
    clickOffsetY.value =  y - imgRect.top;
};

const updateImagePosition = (x, y, rect) => {
  const imgRect = leftRef.value.getBoundingClientRect(); // 实际图片尺寸(包含缩放后)
  const zoom = zoomVal.value / 100;
  const vW = rect.width;                          // 视口尺寸
  const vH = rect.height;
  const iW = leftRef.value.width * zoom;          // 图片尺寸(缩放后)
  const iH = leftRef.value.height * zoom;

  // 图片的x(left), y(top) 缩放偏移, 原始尺寸下总是0
  // 因为缩放后图像 x,y 位置不变, 因此需要一个偏移量来对冲这个变化
  const offX = (iW - leftRef.value.width) / 2;
  const offY = (iH - leftRef.value.height) / 2;
  const iX = x - clickOffsetX.value + offX;
  const iY = y - clickOffsetY.value + offY;

  sliderOffsetX.value = iX;
  updateImagePositionAttribute(iX, iY);
  updateSliderPositionByRatio(sliderRatio.value);

  console.log(
    `update: pox: ${x},${y}, rect: ${rect.left}~${rect.right}:${rect.top}~${rect.bottom}, ` +
    `zoom: ${zoom}, view: ${vW}x${vH}, image: ${iW}x${iH}, ` +
    `ox: ${clickOffsetX.value}, oy: ${clickOffsetY.value}, ofx: ${offX}, ofy: ${offY}, ` +
    `ix: ${iX}, iy: ${iY}`);
}

const updateImageClipPath = (pos) => {
  leftRef.value.style.clipPath = `inset(0 calc(100% - ${pos}px) 0 0)`;
  rightRef.value.style.clipPath = `inset(0 0 0 ${pos}px)`;
};

const updateImageScale = (zoom) => {
  leftRef.value.style.transform = `scale(${zoom})`;
  rightRef.value.style.transform = `scale(${zoom})`;
};

const updateImagePositionAttribute = (x, y) => {

  leftRef.value.style.left = `${x}px`;
  leftRef.value.style.top = `${y}px`;

  rightRef.value.style.left = leftRef.value.style.left;
  rightRef.value.style.top = leftRef.value.style.top;
};

// 重置图像属性
const clearImageAttribute = (imgRef) => {
  imgRef.value.loaded = false;
};
watch(() => props.left, (val) => { clearImageAttribute(leftRef); });
watch(() => props.right, (val) => { clearImageAttribute(rightRef); });

const handleImageLoad = (isLeft) => {
  if (!leftRef.value || !rightRef.value) return;
  if (isLeft)
      leftRef.value.loaded = true;
  else
      rightRef.value.loaded = true;
  if (!leftRef.value.loaded || !rightRef.value.loaded) return;

  const leftArea = leftRef.value.naturalWidth * leftRef.value.naturalHeight;
  const rightArea = rightRef.value.naturalWidth * rightRef.value.naturalHeight;
  if (leftArea != rightArea) {
    // 两个图片可能是不同大小，因此需要调整到相同大小
    // 具体为: 以最大尺寸图 或 右图为基准，同比例缩放另一图片
    if (leftArea > rightArea) {
      imageSize.value.width = leftRef.value.naturalWidth;
      imageSize.value.height = leftRef.value.naturalHeight;
    }
    else {
      imageSize.value.width = rightRef.value.naturalWidth;
      imageSize.value.height = rightRef.value.naturalHeight;
    }

    leftRef.value.width = imageSize.value.width;
    leftRef.value.height = imageSize.value.height;
    rightRef.value.width = imageSize.value.width;
    rightRef.value.height = imageSize.value.height;
  }

  zoomVal.value = 100;
  updateSliderPositionByRatio(0.5);
};

const handleResize = () => {
  if (!viewportRef.value) return;
  updateSliderPositionByRatio(sliderRatio.value);
};

const setFitMode = (mode) => {
  console.log('setFitMode: ', mode);
  zoomVal.value = 100;
  switch (mode) {
    case '1:1':
      leftRef.value.style.objectFit = 'none';
      rightRef.value.style.objectFit = 'none';
      break;

    case 'contain':
      leftRef.value.style.objectFit = 'contain';
      rightRef.value.style.objectFit = 'contain';
      break;

    case 'scale-down':
      leftRef.value.style.objectFit = 'scale-down';
      rightRef.value.style.objectFit = 'scale-down';
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

  .viewport {
    display: flex;
    flex-direction: row;
    position: relative;
    height: 100%;
    overflow: hidden;;

    .image {
      position: absolute;
      left: 0;
      top: 0;

      // top: 50%;
      // transform: translate(0, -50%);

      /* 图像跟随父窗口缩放 */
      width: 100%;
      height: 100%;
      object-fit: contain;
      will-change: transform, clip-path;

      user-select: none;
      cursor: grab;

      &.draging {
        cursor: grabbing;
      }
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