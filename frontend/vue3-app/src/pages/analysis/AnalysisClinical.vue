<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NDataTable, NTag, NSpace, NTabs, NTabPane, NSpin } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

const loading = ref(true);
const activeTab = ref('');

const clinicalData = ref<Record<string, { category: string; count: number; positive: number; rate: number }[]>>({});
const tabLabels = ref<Record<string, string>>({});

onMounted(async () => {
  try {
    const data = await requestJson<{ items: { feature: string; label: string; groups: { category: string; sampleCount: number; positiveCount: number; prevalenceRate: number }[] }[] }>('/analysis/clinical');
    const mapped: Record<string, { category: string; count: number; positive: number; rate: number }[]> = {};
    const labels: Record<string, string> = {};
    for (const item of data.items) {
      mapped[item.feature] = item.groups.map(g => ({
        category: g.category,
        count: g.sampleCount,
        positive: g.positiveCount,
        rate: g.prevalenceRate,
      }));
      labels[item.feature] = item.label;
    }
    clinicalData.value = mapped;
    tabLabels.value = labels;
    const keys = Object.keys(mapped);
    if (keys.length > 0) activeTab.value = keys[0];
  } catch {
    // API not available, keep empty
  } finally {
    loading.value = false;
  }
});

const tabKeys = computed(() => Object.keys(clinicalData.value));
const currentData = computed(() => clinicalData.value[activeTab.value] || []);
const currentLabel = computed(() => tabLabels.value[activeTab.value] || activeTab.value);

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 140, right: 60, top: 20, bottom: 30 },
  xAxis: {
    type: 'value',
    axisLabel: { color: '#64748b', formatter: '{value}%' },
    splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } },
  },
  yAxis: {
    type: 'category',
    data: currentData.value.map(d => d.category),
    axisLabel: { color: '#64748b', width: 130, overflow: 'truncate' },
  },
  series: [{
    type: 'bar',
    data: currentData.value.map(d => ({
      value: +(d.rate * 100).toFixed(1),
      itemStyle: {
        color: d.rate >= 0.3 ? '#ef4444' : d.rate >= 0.15 ? '#f59e0b' : '#06b6d4',
        borderRadius: [0, 6, 6, 0],
      },
    })),
    barWidth: 24,
    label: { show: true, position: 'right', color: '#64748b', formatter: '{c}%' },
  }],
}));

const pieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '65%'],
    data: currentData.value.map((d, i) => ({
      value: d.count,
      name: d.category,
      itemStyle: { color: ['#06b6d4', '#3b82f6', '#f59e0b', '#ef4444'][i % 4] },
    })),
    label: { color: '#64748b', formatter: '{b}\n{d}%' },
  }],
}));

const columns: DataTableColumns = [
  { title: '类别', key: 'category', width: 160 },
  { title: '样本数', key: 'count', width: 120, align: 'right', render: (row: any) => row.count.toLocaleString() },
  { title: '阳性数', key: 'positive', width: 120, align: 'right', render: (row: any) => row.positive.toLocaleString() },
  {
    title: '患病率',
    key: 'rate',
    width: 100,
    align: 'right',
    render: (row: any) => h('span', {
      style: { color: row.rate >= 0.3 ? '#ef4444' : row.rate >= 0.15 ? '#f59e0b' : '#06b6d4', fontWeight: 600 }
    }, (row.rate * 100).toFixed(1) + '%'),
  },
  {
    title: '风险',
    key: 'risk',
    width: 80,
    render: (row: any) => h(NTag, {
      size: 'small',
      type: row.rate >= 0.3 ? 'error' : row.rate >= 0.15 ? 'warning' : 'success',
      bordered: false,
    }, { default: () => row.rate >= 0.3 ? '高' : row.rate >= 0.15 ? '中' : '低' }),
  },
];
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical :size="24">
      <!-- Tabs -->
      <n-card>
        <n-tabs v-model:value="activeTab" type="segment" animated>
          <n-tab-pane v-for="key in tabKeys" :key="key" :name="key" :tab="tabLabels[key] || key" />
        </n-tabs>
      </n-card>

      <!-- Charts -->
      <n-grid :cols="3" :x-gap="16">
        <n-grid-item :span="2">
          <n-card :title="currentLabel + ' — 患病率分布'">
            <EChart :option="chartOption" height="320px" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="样本分布">
            <EChart :option="pieOption" height="320px" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Table -->
      <n-card title="详细数据">
        <n-data-table :columns="columns" :data="currentData" :bordered="false" striped />
      </n-card>
    </n-space>
  </n-spin>
</template>
