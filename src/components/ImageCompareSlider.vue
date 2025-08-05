<template>
  <div class="image-compare-slider">
    <div class="viewport" ref="viewportRef" @mousedown.prevent @wheel.prevent="handleWheel">
      <img :src="left" class="image left" alt="Left" ref="leftRef" @load="handleImageLoad(true)"
        @mousedown.passive="startDrag" @touchstart.passive="startDrag">
      <img :src="right" class="image right" alt="Right" ref="rightRef" @load="handleImageLoad(false)"
        @mousedown.passive="startDrag" @touchstart.passive="startDrag">

      <div class="slider" ref="sliderRef" :style="{ left: `${sliderPosition}px` }"
        @mousedown.passive="(e) => startDrag(e, true)" @touchstart.passive="(e) => startDrag(e, true)">
        <img class="button" src="../assets/icon_button_slider.svg" alt="Slider handle">
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';

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
    default: () => ({ min: 10, max: 400, step: 10 })
  },
});

const emit = defineEmits(['update:zoom'])

const viewportRef = ref(null);
const sliderRef = ref(null);
const leftRef = ref(null);
const rightRef = ref(null);
let imageRef = ref(null);

const sliderPosition = ref(0);
const sliderRatio = ref(0);

const clickOffsetX = ref(0);
const clickOffsetY = ref(0);

const isDragging = ref(false);
const isSliderDragging = ref(false);

const zoomVal = ref(props.zoom);
const zoomMin = ref(props.zoomRange.min);
const zoomMax = ref(props.zoomRange.max);
const zoomStep = ref(props.zoomRange.step);

const clamp = (value, min, max) => {
  return Math.max(min, Math.min(max, value));
};

const handleWheel = (e) => {
  e.preventDefault();

  const viewportRect = viewportRef.value.getBoundingClientRect();
  const mouseXInViewport = e.clientX - viewportRect.left;
  const mouseYInViewport = e.clientY - viewportRect.top;
  const newZoom = clamp(zoomVal.value + (e.deltaY < 0 ? zoomStep.value : -zoomStep.value), zoomMin.value, zoomMax.value);

  updateZoom(newZoom, mouseXInViewport, mouseYInViewport);
};

watch(zoomVal, (newZoom) => {
  emit('update:zoom', newZoom);
});

watch(() => props.zoom, (newZoom) => {
  if (newZoom != zoomVal.value)
    updateZoom(newZoom);
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
    const imageRect = leftRef.value.getBoundingClientRect();
    const ph = clamp(imageRect.width, 10, 60);
    const pv = clamp(imageRect.height, 10, 60);
    const ox = clamp(x - viewportRect.left, ph, viewportRect.width - ph);
    const oy = clamp(y - viewportRect.top,  pv, viewportRect.height - pv);
    updateImagePosition(ox, oy, viewportRect);
  }
};

const updateSliderPosition = (x, rect) => {
  const imageRect = leftRef.value.getBoundingClientRect();
  const left = imageRect.left - rect.left;
  const zoom = zoomVal.value / 100;
  const vW = rect.width;          // viewport width
  const sX = clamp(x, 0, vW);     // slider x
  const sRatio = sX / vW;         // slider x ratio

  const offX = -left;
  const iX = (sX + offX) / zoom;  // slider x on image

  sliderRatio.value = sRatio;
  sliderPosition.value = sX;
  updateImageClipPath(iX);
};

const updateSliderPositionByRatio = (sRatio) => {
  const rect = viewportRef.value.getBoundingClientRect();
  updateSliderPosition(rect.width * sRatio, rect);
};

const getSizeByContain = (size, containerSize) => {
  const ratio = Math.min(containerSize.width / size.width, containerSize.height / size.height);
  return {
    width: size.width * ratio,
    height: size.height * ratio
  };
};

const initImagePositionOffset = (e) => {
  const { x, y } = getPos(e);
  const imgRect = leftRef.value.getBoundingClientRect();

  // 计算点击位置相对于图片的左上角的偏移量
  clickOffsetX.value = x - imgRect.left;
  clickOffsetY.value = y - imgRect.top;
};

const updateImagePosition = (x, y, rect) => {
  const zoom = zoomVal.value / 100;
  const vW = rect.width;                          // 视口尺寸
  const vH = rect.height;
  const iW = leftRef.value.width * zoom;          // 图片尺寸(缩放后), contain 模式下, width 和 height 与视口相同
  const iH = leftRef.value.height * zoom;

  let iX = x - clickOffsetX.value;
  let iY = y - clickOffsetY.value;

  updateImagePositionAttribute(iX, iY);
  updateSliderPositionByRatio(sliderRatio.value);
}

const updateZoom = (newZoom, originX = null, originY = null) => {
  const imageRect = leftRef.value.getBoundingClientRect();
  const viewportRect = viewportRef.value.getBoundingClientRect();
  const left = imageRect.left - viewportRect.left;
  const top = imageRect.top - viewportRect.top

  const mouseXInViewport = originX || (viewportRect.width / 2);
  const mouseYInViewport = originY || (viewportRect.height / 2);

  const oldZoom = zoomVal.value;
  const scaleChange = newZoom / oldZoom;

  // 计算新位置，使鼠标指向的点保持不变
  // 1. 鼠标位置相对于图片的坐标 换算到 此次缩放后 该点距离左上角的长度
  // 2. 该鼠标到图片左上角的长度 减去 鼠标到视口的左上角的长度, 即可得出图片相对于视口的偏移量
  // 3. 由于最后我们需要负的偏移量, 因此交换双方使符号取反 
  const mouseXInImage = mouseXInViewport - left;
  const mouseYInImage = mouseYInViewport - top;
  const newX = mouseXInViewport - (mouseXInImage * scaleChange);
  const newY = mouseYInViewport - (mouseYInImage * scaleChange);

  // 应用更新
  zoomVal.value = newZoom;
  updateImageScale(newZoom / 100);
  updateImagePositionAttribute(newX, newY);
  updateSliderPositionByRatio(sliderRatio.value);
}

const updateImageClipPath = (pos) => {
  leftRef.value.style.clipPath = `inset(0 calc(100% - ${pos}px) 0 0)`;
  rightRef.value.style.clipPath = `inset(0 0 0 ${pos}px)`;
};

const updateImageScale = (zoom) => {
  leftRef.value.style.transform = `scale(${zoom})`;
  rightRef.value.style.transform = leftRef.value.style.transform;
  rightRef.value.style.transformOrigin = leftRef.value.style.transformOrigin;
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

  // 两个图片可能是不同大小，因此需要调整到相同大小
  // 具体为: 以最大尺寸图 或 右图为基准，同比例缩放另一图片
  const leftArea = leftRef.value.naturalWidth * leftRef.value.naturalHeight;
  const rightArea = rightRef.value.naturalWidth * rightRef.value.naturalHeight;

  imageRef = leftRef;
  if (leftArea < rightArea)
    imageRef = rightRef;

  zoomVal.value = 100;
  updateImagePositionAttribute(0, 0);
  updateSliderPositionByRatio(0.5);
};

const handleResize = () => {
  if (!viewportRef.value) return;
  updateSliderPositionByRatio(sliderRatio.value);
};
const resizeObserver = new ResizeObserver(handleResize);

onMounted(() => {
  if (viewportRef.value)
    resizeObserver.observe(viewportRef.value);
});

onBeforeUnmount(() => {
  if (resizeObserver)
    resizeObserver.disconnect();
});

const setFitMode = (mode) => {
  console.log('setFitMode: ', mode);

  const viewportRect = viewportRef.value.getBoundingClientRect();
  const imageSize = {
    width: imageRef.value.naturalWidth,
    height: imageRef.value.naturalHeight
  };
  const vusualSize = getSizeByContain(imageSize, viewportRef.value.getBoundingClientRect());
  const zoomFactor = vusualSize.width / imageSize.width;

  let newZoom;
  switch (mode) {
    case '1:1':
      newZoom = 100 / zoomFactor;
      break;

    case 'contain':
      newZoom = 100;
      break;

    case 'scale-down':
      if (viewportRect.width > imageRef.value.naturalWidth)
        newZoom = 100 / zoomFactor;
      else
        newZoom = 100;
      break;
  }

  updateZoom(newZoom);
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
    overflow: hidden;

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
      transform-origin: 0px 0px;

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