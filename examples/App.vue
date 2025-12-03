<template>
  <div class="container">
    <div class="sidebar" :class="{ 'collapsed': sidebarCollapsed }"
      :style="{ width: sidebarCollapsed ? '0px' : sidebarWidth + 'px' }" ref="sidebarRef">
      <div class="sidebar-handle" :class="{ 'collapsed': sidebarCollapsed }">
        <div class="sidebar-resize" @mousedown="sidebarStartResize"></div>
        <div class="sidebar-toggle" @mousedown="null" @click="sidebarToggle">
          {{ sidebarCollapsed ? '▶' : '◀' }}
        </div>
      </div>

      <div class="sidebar-content">
        <div class="sidebar-controls">
          <label class="hide-first">
            <input type="checkbox" v-model="hideFirstColumn" />
            <span>隐藏第一列(原图)</span>
          </label>
        </div>
        <div class="image-list">
          <div v-for="(row, rowIndex) in imageData" :key="rowIndex" class="row">
            <div v-for="(item, colIndex) in row" :key="colIndex"
              class="item" :class="{ 
                active: itemIndexEquals(currentItemIndex, itemIdexMake(rowIndex, colIndex)), 
                firsts: colIndex === 0,
                hiden: hideFirstColumn && colIndex === 0 }"
              @click="itemClicked(rowIndex, colIndex)">
              <img class="image" :src="getItemImage(item)" :alt="item?.label || item.file" />
              <span class="label">{{ item.label || item.file }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>

    <div class="image-viewer">
      <ImageSliderCompare ref="imageView" :left="currentLeft" :right="currentRight" v-model:zoom="zoom"
        :zoomRange="zoomRange" />

      <div class="controls">
        <el-slider class="zoom" v-model="zoom" :min="zoomRange.min" :max="zoomRange.max" :step="zoomRange.step"
          :vertical="true" height="80px" :format-tooltip="val => `Zoom: ${val.toFixed(2)}%`" />

        <el-dropdown class="fit-mode" @command="mode => imageView.updateFitMode(mode)">
          <el-button plain>
            <el-icon>
              <FullScreen />
            </el-icon>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import ImageSliderCompare from "vue3-image-compare-slider";
import { watch } from "vue";

// 侧边栏
const sidebarWidth = ref(320)
const sidebarMinWidth = 100
const sidebarMaxWidth = 550
const sidebarCollapsed = ref(false)
const hideFirstColumn = ref(false)

const sidebarStartResize = (e) => {
  e.preventDefault()
  const startX = e.clientX
  const startWidth = sidebarWidth.value

  const handleMouseMove = (e) => {
    const dx = e.clientX - startX
    let newWidth = startWidth + dx

    // 限制宽度范围
    if (newWidth < sidebarMinWidth)
      newWidth = sidebarMinWidth
    else if (newWidth > sidebarMaxWidth)
      newWidth = sidebarMaxWidth
    sidebarWidth.value = newWidth;
    sidebarCollapsed.value = newWidth <= sidebarMinWidth;
  }

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const sidebarToggle = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 图片列表
const itemIdexMake = (r, c) => {
  return { row: r, col: c };
}

const itemIndexEquals = (a, b) => {
  return a && b && a.row === b.row && a.col === b.col;
}

const getItemData = (itemIndex) => {
  if (!itemIndex) return null;
  return imageData.value[itemIndex.row][itemIndex.col];
}

const getItemImage = (item) => {
  if (!item) return null;
  if (import.meta.env.BASE_URL !== '/')
    return `${import.meta.env.BASE_URL}/images/${item.file}`;
  return `/images/${item.file}`;
}

const itemClicked = (rowIndex, colIndex) => {
  if (colIndex !== 0)
    currentItemIndex.value = itemIdexMake(rowIndex, colIndex)
}

const currentItemIndex = ref(itemIdexMake(0, 0));
const hoveredItem = ref(null);

// 示例数据
const defaultData = [
  [
    {
      "label": "原图",
      "file": "grayscale/1.jpg",
      "width": 4032,
      "height": 3024,
      "bytes": -1,
      "details": "这是一张美丽的风景照片，拍摄于海边。\n照片包含蓝天、白云和大海。"
    },
    {
      "label": "Flux 1",
      "file": "grayscale/2.jpg",
      "width": 4032,
      "height": 3024,
      "bytes": -1,
      "elapsedTime": 1.5
    },
    {
      "label": "GPT ",
      "file": "grayscale/3.jpg",
      "width": 4032,
      "height": 3024,
      "elapsedTime": 23.5,
      "details": "美化, 上色。"
    },
  ],
  [
    {
      "label": "原图",
      "file": "darksome/1.jpg",
      "width": 1200,
      "height": 900,
      "details": "这是一张暗色系照片，拍摄于夜空。"
    },
    {
      "label": "Flux 1",
      "file": "darksome/2.jpg",
      "width": 1200,
      "height": 900,
      "elapsedTime": 7.5
    }
  ],
  [
    {
      "label": "原图",
      "file": "colour/1.jpg",
      "width": 1024,
      "height": 576,
      "details": ""
    },
    {
      "label": "Flux 1",
      "file": "colour/2.jpg",
      "width": 1024,
      "height": 576,
      "elapsedTime": 7.5
    }
  ]
];

// 尝试加载数据
const loadData = ref(null);
onMounted(async () => {
  try {
    const file = await fetch("data.json");
    loadData.value = await file.json();
  }
  catch (e) {
    console.warn(`load the data.js failed, `, e);
  }
});

// 如果隐藏第一列，且当前选择在第一列，则尝试切换到该行的下一列（如果存在）
watch(hideFirstColumn, (val) => {
  if (val && currentItemIndex.value.col === 0) 
      currentItemIndex.value = itemIdexMake(currentItemIndex.value.row, 1);
});

// 处理数据 - 如果没有传入数据，使用示例数据
const imageData = computed(() => {
  return loadData.value ? loadData.value : defaultData
})

// 视图
const currentLeft = computed(() => getItemImage(getItemData({ row: currentItemIndex.value.row, col: 0 })));
const currentRight = computed(() => getItemImage(getItemData(currentItemIndex.value)));
const imageView = ref(null);
const zoom = ref(100);
const zoomRange = { min: 10, max: 400, step: 10 };
</script>

<style lang="scss" scoped>
.container {
  width: 100%;
  height: 100%;
  background-color: #fff;
  font-size: 12px;

  display: flex;
  flex-direction: row;
  gap: 0.2rem;

  .sidebar {
    position: relative;

    &.collapsed .sidebar-content {
      display: none;
    }

    .sidebar-handle {
      z-index: 10;
      position: absolute;
      top: 0px;
      right: -4px;
      width: 4px;
      height: 100%;
      background-color: #ddd8;
      transition: background-color 0.2s;

      &.collapsed {
        background-color: transparent;
      }

      &:hover {
        background-color: #ccca;
      }

      .sidebar-resize {
        width: 100%;
        height: 100%;
        cursor: ew-resize;
      }

      .sidebar-toggle {
        position: absolute;
        top: 50%;
        left: 4px;
        transform: translateY(-50%);
        height: 60px;
        border: 1px solid #888;
        border-radius: 4px;
        align-content: center;
        cursor: pointer;

        background-color: #ddd8;
        color: #333;

        &hover {
          background-color: #ccca;
        }
      }
    }

    .sidebar-content {
      height: 100%;
    }

    .sidebar-controls {
      padding: 0.5rem;
      .hide-first {
        cursor: pointer;
        display: flex;
        gap: 0.2rem;
      }
    }

    .image-list {
      height: 100%;
      padding: 3px 3px;
      display: flex;
      flex-direction: column;
      overflow: auto;

      .row {
        gap: 0.2rem;
        display: flex;
        flex-wrap: nowrap;
        min-width: min-content;

        .item {
          display: flex;
          flex-direction: column;
          align-items: center;
          cursor: pointer;
          transition: all 0.2s ease;
          padding: 0.2rem;
          width: 100px;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
          }

          &.firsts {
            pointer-events: none;
            cursor: default;
            opacity: 0.9;
            border-right: 2px solid #888;
          }

          &.firsts:hover {
            transform: none;
            box-shadow: none;
          }

          &.firsts.active {
            background-color: inherit;
            box-shadow: none;
          }

          &.hiden {
            display: none;
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

          .label {
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: #424242;
            text-align: center;
            word-break: break-word;
          }
        }
      }
    }
  }

  .image-viewer {
    flex-grow: 1;
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
}
</style>