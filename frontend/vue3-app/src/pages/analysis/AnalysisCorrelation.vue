<script setup lang="ts">
import { computed, ref, h, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NSpace, NDataTable, NTag, NSpin } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

// Try loading from API; fall back to static defaults
const features = ref(['年龄', 'BMI', '吸烟', '饮酒', '运动', '睡眠', '心理健康', '身体健康', '行走困难', '中风', '糖尿病', '肾病']);

const correlationMatrix = ref([
  [1.00, 0.12, 0.08, -0.05, -0.15, -0.08, 0.10, 0.22, 0.35, 0.25, 0.28, 0.20],
  [0.12, 1.00, 0.03, -0.08, -0.12, -0.04, 0.06, 0.15, 0.18, 0.08, 0.22, 0.10],
  [0.08, 0.03, 1.00, 0.15, -0.08, -0.06, 0.12, 0.10, 0.05, 0.10, 0.06, 0.04],
  [-0.05, -0.08, 0.15, 1.00, 0.02, -0.03, 0.08, -0.02, -0.05, -0.02, -0.04, -0.03],
  [-0.15, -0.12, -0.08, 0.02, 1.00, 0.05, -0.10, -0.18, -0.22, -0.08, -0.12, -0.06],
  [-0.08, -0.04, -0.06, -0.03, 0.05, 1.00, -0.15, -0.10, -0.08, -0.04, -0.05, -0.03],
  [0.10, 0.06, 0.12, 0.08, -0.10, -0.15, 1.00, 0.35, 0.15, 0.08, 0.10, 0.06],
  [0.22, 0.15, 0.10, -0.02, -0.18, -0.10, 0.35, 1.00, 0.42, 0.18, 0.20, 0.15],
  [0.35, 0.18, 0.05, -0.05, -0.22, -0.08, 0.15, 0.42, 1.00, 0.22, 0.25, 0.18],
  [0.25, 0.08, 0.10, -0.02, -0.08, -0.04, 0.08, 0.18, 0.22, 1.00, 0.15, 0.20],
  [0.28, 0.22, 0.06, -0.04, -0.12, -0.05, 0.10, 0.20, 0.25, 0.15, 1.00, 0.18],
  [0.20, 0.10, 0.04, -0.03, -0.06, -0.03, 0.06, 0.15, 0.18, 0.20, 0.18, 1.00],
]);

const loading = ref(true);

onMounted(async () => {
  try {
    const data = await requestJson<{ features: string[]; matrix: number[][] }>('/analysis/correlation');
    if (data.features?.length && data.matrix?.length) {
      features.value = data.features;
      correlationMatrix.value = data.matrix;
    }
  } catch {
    // API not available, use defaults
  } finally {
    loading.value = false;
  }
});

const heatmapData = computed(() => {
  const result: [number, number, number][] = [];
  for (let i = 0; i < features.value.length; i++) {
    for (let j = 0; j < features.value.length; j++) {
      result.push([j, i, correlationMatrix.value[i][j]]);
    }
  }
  return result;
});

const heatmapOption = computed(() => ({
  tooltip: {
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: 'rgba(51, 65, 85, 0.5)',
    textStyle: { color: '#e2e8f0' },
    formatter: (p: any) => `<b>${features.value[p.value[1]]} x ${features.value[p.value[0]]}</b><br/>相关系数: <b>${p.value[2].toFixed(2)}</b>`,
  },
  grid: { left: 90, right: 80, top: 20, bottom: 80 },
  xAxis: {
    type: 'category',
    data: features.value,
    axisLabel: { color: '#94a3b8', rotate: 45, fontSize: 11 },
    splitArea: { show: true, areaStyle: { color: ['rgba(30,41,59,0.25)', 'rgba(15,23,42,0.25)'] } },
  },
  yAxis: {
    type: 'category',
    data: features.value,
    axisLabel: { color: '#94a3b8', fontSize: 11 },
    splitArea: { show: true, areaStyle: { color: ['rgba(30,41,59,0.25)', 'rgba(15,23,42,0.25)'] } },
  },
  visualMap: {
    min: -0.5,
    max: 1,
    calculable: true,
    orient: 'vertical',
    right: 10,
    top: 'center',
    inRange: {
      color: ['#3b82f6', '#1e293b', '#fef3c7', '#fbbf24', '#ef4444'],
    },
    textStyle: { color: '#94a3b8' },
  },
  series: [{
    type: 'heatmap',
    data: heatmapData.value,
    label: { show: true, color: '#cbd5e1', fontSize: 9, formatter: (p: any) => p.value[2].toFixed(2) },
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(6, 182, 212, 0.4)' } },
  }],
}));

const topCorrelations = computed(() => {
  const pairs: { f1: string; f2: string; corr: number }[] = [];
  for (let i = 0; i < features.value.length; i++) {
    for (let j = i + 1; j < features.value.length; j++) {
      pairs.push({ f1: features.value[i], f2: features.value[j], corr: correlationMatrix.value[i][j] });
    }
  }
  return pairs.sort((a, b) => Math.abs(b.corr) - Math.abs(a.corr)).slice(0, 10);
});

const topColumns: DataTableColumns = [
  {
    title: '排名',
    key: 'rank',
    width: 60,
    align: 'center',
    render: (_row: any, index: number) => h(NTag, {
      size: 'small',
      type: index < 3 ? 'warning' : 'default',
      bordered: false,
    }, { default: () => index + 1 }),
  },
  { title: '特征 1', key: 'f1', width: 100 },
  { title: '特征 2', key: 'f2', width: 100 },
  {
    title: '相关系数',
    key: 'corr',
    width: 120,
    align: 'right',
    render: (row: any) => h('span', {
      style: { color: row.corr > 0 ? '#ef4444' : '#3b82f6', fontWeight: 600, fontFamily: 'monospace' },
    }, (row.corr > 0 ? '+' : '') + row.corr.toFixed(2)),
  },
  {
    title: '方向',
    key: 'direction',
    width: 80,
    render: (row: any) => h(NTag, {
      size: 'small',
      type: row.corr > 0 ? 'error' : 'info',
      bordered: false,
    }, { default: () => row.corr > 0 ? '正相关' : '负相关' }),
  },
];
</script>

<template>
  <n-spin :show="loading">
  <n-space vertical :size="24">
    <!-- Charts row -->
    <n-grid :cols="12" :x-gap="16">
      <n-grid-item :span="7">
        <n-card title="相关性热力图">
          <EChart :option="heatmapOption" height="520px" />
        </n-card>
      </n-grid-item>
      <n-grid-item :span="5">
        <n-space vertical :size="16">
          <n-card title="Top 10 强相关特征对">
            <n-data-table :columns="topColumns" :data="topCorrelations" :bordered="false" striped size="small" />
          </n-card>
          <n-card style="background: rgba(6,182,212,0.03); border-color: rgba(6,182,212,0.2);">
            <template #header>
              <span style="color: #67e8f9;">分析说明</span>
            </template>
            <n-grid :cols="2" :x-gap="16" :y-gap="8">
              <n-grid-item>
                <n-space align="center" :size="8">
                  <span style="display: inline-block; width: 12px; height: 6px; border-radius: 3px; background: linear-gradient(to right, #f59e0b, #ef4444);"></span>
                  <span style="font-size: 13px; color: #94a3b8;">正相关：同向变化</span>
                </n-space>
              </n-grid-item>
              <n-grid-item>
                <n-space align="center" :size="8">
                  <span style="display: inline-block; width: 12px; height: 6px; border-radius: 3px; background: linear-gradient(to right, #3b82f6, #60a5fa);"></span>
                  <span style="font-size: 13px; color: #94a3b8;">负相关：反向变化</span>
                </n-space>
              </n-grid-item>
              <n-grid-item>
                <span style="font-size: 13px; color: #94a3b8;">|r| > 0.3 为中等以上相关</span>
              </n-grid-item>
              <n-grid-item>
                <span style="font-size: 13px; color: #94a3b8;">身体健康↔行走困难 最强</span>
              </n-grid-item>
            </n-grid>
          </n-card>
        </n-space>
      </n-grid-item>
    </n-grid>
  </n-space>
  </n-spin>
</template>
