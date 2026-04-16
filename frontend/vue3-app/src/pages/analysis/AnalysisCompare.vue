<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NStatistic, NDataTable, NTag, NSpace, NSpin } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

const loading = ref(true);

const datasets = ref<{ name: string; rows: number; cols: number; positive: number; rate: number; auc: number }[]>([]);

onMounted(async () => {
  try {
    const data = await requestJson<{ modelAuc: number; datasets: { name: string; rows: number; columns: number; positiveCount?: number; prevalenceRate?: number }[] }>('/dashboard/overview');
    datasets.value = data.datasets.map(ds => ({
      name: ds.name,
      rows: ds.rows,
      cols: ds.columns,
      positive: ds.positiveCount || 0,
      rate: ds.prevalenceRate || 0,
      auc: data.modelAuc || 0,
    }));
  } catch {
    // API not available, keep empty
  } finally {
    loading.value = false;
  }
});

const selectedDatasets = ref<string[]>([]);

// Auto-select first two datasets when data loads
const effectiveSelected = computed(() => {
  if (selectedDatasets.value.length > 0) return selectedDatasets.value;
  return datasets.value.slice(0, 2).map(d => d.name);
});

const comparisonOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { top: 5, textStyle: { color: '#64748b' } },
  grid: { left: 50, right: 30, top: 50, bottom: 30 },
  xAxis: {
    type: 'category',
    data: ['样本量(k)', '特征数', '患病率(%)', 'AUC×100'],
    axisLabel: { color: '#64748b' },
  },
  yAxis: { type: 'value', axisLabel: { color: '#64748b' }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } } },
  series: effectiveSelected.value.map((name, i) => {
    const d = datasets.value.find(dd => dd.name === name);
    if (!d) return { name, type: 'bar', data: [], barWidth: 28 };
    return {
      name,
      type: 'bar',
      data: [+(d.rows / 1000).toFixed(1), d.cols, +(d.rate * 100).toFixed(1), +(d.auc * 100).toFixed(1)],
      itemStyle: { color: ['#06b6d4', '#3b82f6', '#f59e0b', '#ef4444'][i], borderRadius: [4, 4, 0, 0] },
      barWidth: 28,
    };
  }),
}));

const radarOption = computed(() => ({
  radar: {
    indicator: [
      { name: '数据规模', max: 100 },
      { name: '特征丰富度', max: 100 },
      { name: '患病率', max: 100 },
      { name: '模型AUC', max: 100 },
      { name: '数据质量', max: 100 },
    ],
    shape: 'polygon',
    splitArea: { areaStyle: { color: ['rgba(30,41,59,0.3)', 'rgba(15,23,42,0.3)'] } },
    axisName: { color: '#64748b' },
  },
  legend: { bottom: 0, textStyle: { color: '#64748b' } },
  series: [{
    type: 'radar',
    data: datasets.value.slice(0, 3).map((d, i) => {
      const maxRows = Math.max(...datasets.value.map(dd => dd.rows), 1);
      const maxCols = Math.max(...datasets.value.map(dd => dd.cols), 1);
      const colors = ['#06b6d4', '#3b82f6', '#f59e0b', '#ef4444'];
      return {
        value: [
          Math.round((d.rows / maxRows) * 100),
          Math.round((d.cols / maxCols) * 100),
          Math.round(d.rate * 100),
          Math.round(d.auc * 100),
          Math.round(Math.min(d.rows / 1000, 100)),
        ],
        name: d.name,
        lineStyle: { color: colors[i] },
        itemStyle: { color: colors[i] },
        areaStyle: { color: colors[i].replace(')', ', 0.1)').replace('rgb', 'rgba') },
      };
    }),
  }],
}));

const columns: DataTableColumns = [
  { title: '数据集', key: 'name', width: 140 },
  { title: '样本量', key: 'rows', width: 120, align: 'right', render: (row: any) => row.rows.toLocaleString() },
  { title: '特征数', key: 'cols', width: 80, align: 'right' },
  {
    title: '患病率',
    key: 'rate',
    width: 100,
    align: 'right',
    render: (row: any) => h('span', {
      style: { color: row.rate > 0.3 ? '#ef4444' : '#06b6d4', fontWeight: 600 },
    }, (row.rate * 100).toFixed(1) + '%'),
  },
  {
    title: 'AUC',
    key: 'auc',
    width: 100,
    align: 'right',
    render: (row: any) => h('span', {
      style: { color: '#22c55e', fontWeight: 600 },
    }, row.auc.toFixed(3)),
  },
];

const toggleDataset = (name: string) => {
  if (selectedDatasets.value.length === 0) {
    // Initialize from effective
    selectedDatasets.value = [...effectiveSelected.value];
  }
  if (selectedDatasets.value.includes(name)) {
    selectedDatasets.value = selectedDatasets.value.filter(n => n !== name);
  } else {
    selectedDatasets.value.push(name);
  }
};
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical :size="24">
      <!-- Dataset cards -->
      <n-grid :cols="4" :x-gap="16" :y-gap="16">
        <n-grid-item v-for="ds in datasets" :key="ds.name">
          <n-card
            :style="{
              cursor: 'pointer',
              borderColor: effectiveSelected.includes(ds.name) ? 'rgba(6,182,212,0.5)' : undefined,
              boxShadow: effectiveSelected.includes(ds.name) ? '0 0 0 2px rgba(6,182,212,0.2)' : undefined,
            }"
            @click="toggleDataset(ds.name)"
          >
            <template #header>
              <n-space align="center" justify="space-between">
                <span>{{ ds.name }}</span>
                <n-tag v-if="effectiveSelected.includes(ds.name)" type="info" size="small" :bordered="false">已选</n-tag>
              </n-space>
            </template>
            <n-grid :cols="2" :x-gap="8" :y-gap="8">
              <n-grid-item>
                <n-statistic label="样本" :value="ds.rows" tabular-nums />
              </n-grid-item>
              <n-grid-item>
                <n-statistic label="特征" :value="ds.cols" tabular-nums />
              </n-grid-item>
              <n-grid-item>
                <n-statistic label="患病率" tabular-nums>
                  <template #default>
                    <span :style="{ color: ds.rate > 0.3 ? '#ef4444' : '#06b6d4' }">{{ (ds.rate * 100).toFixed(1) }}%</span>
                  </template>
                </n-statistic>
              </n-grid-item>
              <n-grid-item>
                <n-statistic label="AUC" tabular-nums>
                  <template #default>
                    <span style="color: #22c55e;">{{ ds.auc.toFixed(3) }}</span>
                  </template>
                </n-statistic>
              </n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Charts -->
      <n-grid :cols="2" :x-gap="16">
        <n-grid-item>
          <n-card title="多维度柱状对比">
            <EChart :option="comparisonOption" height="350px" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="综合能力雷达图">
            <EChart :option="radarOption" height="350px" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Insight cards -->
      <n-grid :cols="3" :x-gap="16">
        <n-grid-item>
          <n-card style="background: rgba(6,182,212,0.03); border-color: rgba(6,182,212,0.2);">
            <template #header>
              <span style="color: #67e8f9; font-size: 14px;">数据规模差异</span>
            </template>
            <span style="font-size: 12px; color: #22d3ee; line-height: 1.6;">Kaggle 数据集样本量远超 UCI (31万 vs 303)，更适合深度学习和复杂模型训练，但 UCI 数据集临床指标更精确。</span>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card style="background: rgba(245,158,11,0.03); border-color: rgba(245,158,11,0.2);">
            <template #header>
              <span style="color: #fcd34d; font-size: 14px;">患病率差异</span>
            </template>
            <span style="font-size: 12px; color: #fbbf24; line-height: 1.6;">UCI Cleveland 患病率 45.9%，远高于 Kaggle 的 8.6%。UCI 数据偏向临床就诊人群，存在选择偏差。</span>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card style="background: rgba(34,197,94,0.03); border-color: rgba(34,197,94,0.2);">
            <template #header>
              <span style="color: #86efac; font-size: 14px;">模型表现对比</span>
            </template>
            <span style="font-size: 12px; color: #4ade80; line-height: 1.6;">Kaggle 2020 数据集 AUC 最高(0.912)，主要得益于大样本量和特征质量。建议以此作为主训练集。</span>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Table -->
      <n-card title="数据集详情">
        <n-data-table :columns="columns" :data="datasets" :bordered="false" striped />
      </n-card>
    </n-space>
  </n-spin>
</template>
