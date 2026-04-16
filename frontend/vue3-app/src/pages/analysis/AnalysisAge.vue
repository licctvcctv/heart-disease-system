<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NStatistic, NDataTable, NTag, NSpace, NSpin } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

const loading = ref(true);

const ageData = ref<any[]>([]);

onMounted(async () => {
  try {
    const data = await requestJson<{ items: any[] }>('/analysis/age');
    ageData.value = data.items.map(d => ({ group: d.ageGroup, total: d.sampleCount, positive: d.positiveCount, rate: d.prevalenceRate }));
  } catch {
    // API not available, keep empty
  } finally {
    loading.value = false;
  }
});

const totalSamples = computed(() => ageData.value.reduce((s, d) => s + d.total, 0));
const totalPositive = computed(() => ageData.value.reduce((s, d) => s + d.positive, 0));
const avgRate = computed(() => totalSamples.value > 0 ? ((totalPositive.value / totalSamples.value) * 100).toFixed(1) : '0.0');
const highRiskGroup = computed(() => ageData.value.length > 0 ? [...ageData.value].sort((a, b) => b.rate - a.rate)[0] : { group: '-', rate: 0 });

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 60, right: 40, top: 50, bottom: 50 },
  legend: { top: 8, textStyle: { color: '#aaa' } },
  xAxis: {
    type: 'category',
    data: ageData.value.map(d => d.group),
    axisLabel: { color: '#888', rotate: 30 },
  },
  yAxis: [
    { type: 'value', name: '样本数', axisLabel: { color: '#888' }, splitLine: { lineStyle: { color: '#333' } } },
    { type: 'value', name: '患病率', axisLabel: { color: '#888', formatter: '{value}%' }, splitLine: { show: false } },
  ],
  series: [
    { name: '总样本', type: 'bar', data: ageData.value.map(d => d.total), itemStyle: { color: '#06b6d4', borderRadius: [4, 4, 0, 0] }, barWidth: 18 },
    { name: '阳性', type: 'bar', data: ageData.value.map(d => d.positive), itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] }, barWidth: 18 },
    { name: '患病率', type: 'line', yAxisIndex: 1, data: ageData.value.map(d => +(d.rate * 100).toFixed(1)), lineStyle: { color: '#f59e0b', width: 3 }, itemStyle: { color: '#f59e0b' }, symbol: 'circle', symbolSize: 8 },
  ],
}));

const pieOption = computed(() => {
  // Group age data into buckets
  const young = ageData.value.filter(d => {
    const n = parseInt(d.group);
    return n < 40 || d.group.startsWith('18') || d.group.startsWith('25') || d.group.startsWith('30') || d.group.startsWith('35');
  });
  const middle = ageData.value.filter(d => {
    const n = parseInt(d.group);
    return n >= 40 && n < 55;
  });
  const middleOld = ageData.value.filter(d => {
    const n = parseInt(d.group);
    return n >= 55 && n < 70;
  });
  const old = ageData.value.filter(d => {
    const n = parseInt(d.group);
    return n >= 70 || d.group.includes('80');
  });

  const sum = (arr: any[]) => arr.reduce((s, d) => s + d.total, 0);

  return {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      data: [
        { value: sum(young), name: '青年(18-39)', itemStyle: { color: '#06b6d4' } },
        { value: sum(middle), name: '中年(40-54)', itemStyle: { color: '#3b82f6' } },
        { value: sum(middleOld), name: '中老年(55-69)', itemStyle: { color: '#f59e0b' } },
        { value: sum(old), name: '老年(70+)', itemStyle: { color: '#ef4444' } },
      ].filter(d => d.value > 0),
      label: { color: '#aaa', formatter: '{b}\n{d}%' },
    }],
  };
});

const columns: DataTableColumns = [
  { title: '年龄段', key: 'group', width: 100 },
  { title: '总样本', key: 'total', width: 120, align: 'right', render: (row: any) => row.total.toLocaleString() },
  { title: '阳性数', key: 'positive', width: 120, align: 'right', render: (row: any) => row.positive.toLocaleString() },
  {
    title: '患病率',
    key: 'rate',
    width: 100,
    align: 'right',
    render: (row: any) => h('span', {
      style: { color: row.rate >= 0.15 ? '#ef4444' : row.rate >= 0.08 ? '#f59e0b' : '#22c55e', fontWeight: 600 }
    }, (row.rate * 100).toFixed(1) + '%'),
  },
  {
    title: '风险等级',
    key: 'risk',
    width: 100,
    render: (row: any) => h(NTag, {
      size: 'small',
      type: row.rate >= 0.15 ? 'error' : row.rate >= 0.08 ? 'warning' : 'success',
      bordered: false,
    }, { default: () => row.rate >= 0.15 ? '高风险' : row.rate >= 0.08 ? '中风险' : '低风险' }),
  },
];
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical :size="24">
      <!-- KPI Cards -->
      <n-grid :cols="4" :x-gap="16" :y-gap="16">
        <n-grid-item>
          <n-card>
            <n-statistic label="总样本数" :value="totalSamples" tabular-nums>
              <template #suffix>
                <span style="font-size: 14px; color: #06b6d4;"> 条</span>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="阳性总数" :value="totalPositive" tabular-nums>
              <template #prefix>
                <span style="color: #ef4444;">●</span>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="平均患病率" tabular-nums>
              <template #default>
                <span style="color: #f59e0b;">{{ avgRate }}%</span>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="最高风险年龄" tabular-nums>
              <template #default>
                <span style="color: #ef4444;">{{ highRiskGroup.group }}</span>
              </template>
              <template #suffix>
                <n-tag type="error" size="small" :bordered="false">{{ (highRiskGroup.rate * 100).toFixed(1) }}%</n-tag>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Charts -->
      <n-grid :cols="5" :x-gap="16">
        <n-grid-item :span="3">
          <n-card title="各年龄段样本数与患病率">
            <EChart :option="barOption" height="400px" />
          </n-card>
        </n-grid-item>
        <n-grid-item :span="2">
          <n-card title="年龄段分组占比">
            <EChart :option="pieOption" height="400px" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Table -->
      <n-card title="详细数据">
        <n-data-table :columns="columns" :data="ageData" :bordered="false" striped />
      </n-card>
    </n-space>
  </n-spin>
</template>
