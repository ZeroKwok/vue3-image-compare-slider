# vue3-image-compare-slider  

A simple image compare slider component for Vue 3, supporting zooming, dragging and fit modes.  

[Online Demo](https://zerokwok.github.io/vue3-image-compare-slider/index.html)

## Features  

- Supports zooming, dragging, and slider position adjustment  
- Supports fit modes (1:1, contain, scale-down)  

## Installation  

```bash  
npm install vue3-image-compare-slider  
```  

## Usage  

### Global Registration  

```js  
import { createApp } from 'vue'  
import ImageCompareSlider, { install } from 'vue3-image-compare-slider'  

const app = createApp(App)  
app.use(install)  
```  

### Usage in Components  

```vue  
<template>  
  <ImageCompareSlider  
    :left="leftImage"  
    :right="rightImage"  
    v-model:zoom="zoom"  
    :zoomRange="{ min: 10, max: 400, step: 10 }"  
  />  
</template>  

<script setup>  
import { ref } from 'vue'  
import ImageCompareSlider from 'vue3-image-compare-slider'  

const leftImage = ref('left.jpg')  
const rightImage = ref('right.jpg')  
const zoom = ref(100)  
</script>  
```  

## Props  

| Prop       | Type    | Default               | Description          |  
| ---------- | ------- | --------------------- | -------------------- |  
| left       | String  | Required              | Left image URL       |  
| right      | String  | Required              | Right image URL      |  
| zoom       | Number  | 100                   | Zoom percentage      |  
| zoomRange  | Object  | {min:10,max:400,step:10} | Zoom range settings  |  

## Slots  

None  

## Events  

| Event Name      | Description                | Callback Parameters |  
| --------------- | -------------------------- | ------------------- |  
| update:zoom     | Triggered on zoom change   | New zoom value      |  

## Methods  

Callable via `ref`:  

| Method         | Description                | Parameters         |  
| -------------- | -------------------------- | ------------------ |  
| setFitMode     | Set the fit mode           | '1:1' \| 'contain' \| 'scale-down' |  

## Example  

View the complete example in [examples/App.vue](examples/App.vue) or [online demo](https://zerokwok.github.io/vue3-image-compare-slider/index.html).  

## Preview  

Run the example:

```bash
cd vue3-image-compare-slider
yarn && yarn dev
```
