<script setup lang="ts">
import * as echarts from 'echarts';
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';

const props = defineProps<{
  option: Record<string, unknown>;
  height?: string;
}>();

const chartEl = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let observer: ResizeObserver | null = null;
const handleResize = () => chart?.resize();

const syncOption = () => {
  if (!chart) {
    return;
  }
  chart.setOption(props.option, true);
};

onMounted(() => {
  if (!chartEl.value) {
    return;
  }
  chart = echarts.init(chartEl.value, undefined, { renderer: 'canvas' });
  chart.setOption(props.option);
  observer = new ResizeObserver(() => chart?.resize());
  observer.observe(chartEl.value);
  window.addEventListener('resize', handleResize);
});

watch(
  () => props.option,
  () => {
    syncOption();
  },
  { deep: true },
);

onBeforeUnmount(() => {
  observer?.disconnect();
  window.removeEventListener('resize', handleResize);
  chart?.dispose();
  chart = null;
});
</script>

<template>
  <div ref="chartEl" class="echart" :style="{ height: height || '100%' }" />
</template>
