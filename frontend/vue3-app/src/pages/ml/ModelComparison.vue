<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NSpace, NStatistic, NTag, NSpin } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

const loading = ref(true);

const models = ref<{ name: string; accuracy: number; precision: number; recall: number; f1: number; auc: number }[]>([]);

onMounted(async () => {
  try {
    const data = await requestJson<{ models: { name: string; accuracy: number; precision: number; recall: number; f1: number; auc: number }[] }>('/model/metrics');
    models.value = data.models;
  } catch {
    // API not available, keep empty
  } finally {
    loading.value = false;
  }
});

const metricsOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(51, 65, 85, 0.5)', textStyle: { color: '#e2e8f0' } },
  legend: { top: 5, textStyle: { color: '#64748b' } },
  grid: { left: 50, right: 20, top: 50, bottom: 30 },
  xAxis: {
    type: 'category',
    data: models.value.map(m => m.name),
    axisLabel: { color: '#64748b' },
  },
  yAxis: { type: 'value', min: 0.7, max: 1, axisLabel: { color: '#64748b' }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } } },
  series: [
    { name: 'Accuracy', type: 'bar', data: models.value.map(m => m.accuracy), itemStyle: { color: '#06b6d4', borderRadius: [4, 4, 0, 0] }, barWidth: 16 },
    { name: 'Precision', type: 'bar', data: models.value.map(m => m.precision), itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, barWidth: 16 },
    { name: 'Recall', type: 'bar', data: models.value.map(m => m.recall), itemStyle: { color: '#f59e0b', borderRadius: [4, 4, 0, 0] }, barWidth: 16 },
    { name: 'F1', type: 'bar', data: models.value.map(m => m.f1), itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, barWidth: 16 },
    { name: 'AUC', type: 'bar', data: models.value.map(m => m.auc), itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] }, barWidth: 16 },
  ],
}));

const radarOption = computed(() => {
  const colors = ['#06b6d4', '#3b82f6', '#f59e0b', '#22c55e', '#ef4444', '#8b5cf6'];
  return {
    radar: {
      indicator: [
        { name: 'Accuracy', max: 1 },
        { name: 'Precision', max: 1 },
        { name: 'Recall', max: 1 },
        { name: 'F1', max: 1 },
        { name: 'AUC', max: 1 },
      ],
      shape: 'polygon',
      splitArea: { areaStyle: { color: ['rgba(30,41,59,0.3)', 'rgba(15,23,42,0.3)'] } },
      axisName: { color: '#64748b' },
    },
    legend: { bottom: 0, textStyle: { color: '#64748b' } },
    series: [{
      type: 'radar',
      data: models.value.map((m, i) => ({
        value: [m.accuracy, m.precision, m.recall, m.f1, m.auc],
        name: m.name,
        lineStyle: { color: colors[i % colors.length] },
        itemStyle: { color: colors[i % colors.length] },
        areaStyle: { color: colors[i % colors.length].replace(')', ', 0.12)').replace('#', 'rgba(').replace(/([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/, (_, r, g, b) => `${parseInt(r, 16)}, ${parseInt(g, 16)}, ${parseInt(b, 16)}`) },
      })),
    }],
  };
});

const rocOption = computed(() => {
  const colors = ['#06b6d4', '#3b82f6', '#f59e0b', '#22c55e', '#ef4444', '#8b5cf6'];
  // Generate approximate ROC curve points based on AUC
  const generateRoc = (auc: number) => {
    const points: [number, number][] = [[0, 0]];
    const steps = [0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 1];
    for (const fpr of steps) {
      const tpr = Math.min(1, Math.pow(fpr, 1 - auc) * auc + (1 - Math.pow(1 - fpr, auc)) * (1 - auc / 2));
      points.push([fpr, +tpr.toFixed(2)]);
    }
    return points;
  };

  return {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(51, 65, 85, 0.5)', textStyle: { color: '#e2e8f0' } },
    legend: { top: 5, textStyle: { color: '#64748b' } },
    grid: { left: 50, right: 20, top: 50, bottom: 40 },
    xAxis: { type: 'value', name: 'FPR', min: 0, max: 1, axisLabel: { color: '#64748b' }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } } },
    yAxis: { type: 'value', name: 'TPR', min: 0, max: 1, axisLabel: { color: '#64748b' }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } } },
    series: [
      ...models.value.map((m, i) => ({
        name: `${m.name} (${m.auc.toFixed(3)})`,
        type: 'line' as const,
        smooth: true,
        data: generateRoc(m.auc),
        lineStyle: { color: colors[i % colors.length], width: 2 },
        symbol: 'none' as const,
      })),
      { name: '随机基线', type: 'line' as const, data: [[0, 0], [1, 1]], lineStyle: { color: '#cbd5e1', type: 'dashed' as const, width: 1 }, symbol: 'none' as const },
    ],
  };
});

const bestModel = computed(() => models.value.length > 0 ? models.value.reduce((best, m) => m.auc > best.auc ? m : best) : { name: '-', accuracy: 0, precision: 0, recall: 0, f1: 0, auc: 0 });
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical :size="24">
      <!-- KPI Cards -->
      <n-grid :cols="4" :x-gap="16" :y-gap="16">
        <n-grid-item v-for="m in models" :key="m.name">
          <n-card>
            <template #header-extra>
              <n-tag v-if="m === bestModel" type="warning" size="small" :bordered="false">最优</n-tag>
            </template>
            <n-statistic :label="m.name" tabular-nums>
              <template #default>
                <span style="font-size: 28px;">{{ m.auc.toFixed(3) }}</span>
              </template>
              <template #suffix>
                <span style="font-size: 13px; color: #999;">AUC</span>
              </template>
            </n-statistic>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 12px; font-size: 12px;">
              <div><span style="color: #999;">Acc</span> <span style="font-weight: 600; margin-left: 4px;">{{ m.accuracy.toFixed(3) }}</span></div>
              <div><span style="color: #999;">Pre</span> <span style="font-weight: 600; margin-left: 4px;">{{ m.precision.toFixed(3) }}</span></div>
              <div><span style="color: #999;">Rec</span> <span style="font-weight: 600; margin-left: 4px;">{{ m.recall.toFixed(3) }}</span></div>
              <div><span style="color: #999;">F1</span> <span style="font-weight: 600; margin-left: 4px;">{{ m.f1.toFixed(3) }}</span></div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Charts row -->
      <n-grid :cols="2" :x-gap="16">
        <n-grid-item>
          <n-card title="指标柱状对比">
            <EChart :option="metricsOption" height="350px" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="综合能力雷达图">
            <EChart :option="radarOption" height="350px" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- ROC -->
      <n-card title="ROC 曲线对比">
        <template #header-extra>
          <n-tag type="info" size="small" :bordered="false">最优模型: {{ bestModel.name }} (AUC {{ bestModel.auc.toFixed(3) }})</n-tag>
        </template>
        <EChart :option="rocOption" height="400px" />
      </n-card>
    </n-space>
  </n-spin>
</template>
