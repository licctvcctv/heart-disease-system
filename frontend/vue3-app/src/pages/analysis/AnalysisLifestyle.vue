<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NStatistic, NDataTable, NTag, NSpace, NSpin } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

const loading = ref(true);

const factors = ref<{ name: string; yes: { count: number; rate: number }; no: { count: number; rate: number } }[]>([]);

onMounted(async () => {
  try {
    const data = await requestJson<{ items: { factor: string; category: string; sampleCount: number; positiveCount: number; prevalenceRate: number }[] }>('/analysis/lifestyle');
    const grouped: Record<string, { yes?: { count: number; rate: number }; no?: { count: number; rate: number } }> = {};
    for (const item of data.items) {
      if (!grouped[item.factor]) grouped[item.factor] = {};
      const cat = item.category.toLowerCase();
      if (cat === 'yes' || cat === '是') {
        grouped[item.factor].yes = { count: item.sampleCount, rate: item.prevalenceRate };
      } else if (cat === 'no' || cat === '否') {
        grouped[item.factor].no = { count: item.sampleCount, rate: item.prevalenceRate };
      } else {
        if (!grouped[item.factor].yes) {
          grouped[item.factor].yes = { count: item.sampleCount, rate: item.prevalenceRate };
        } else if (!grouped[item.factor].no) {
          grouped[item.factor].no = { count: item.sampleCount, rate: item.prevalenceRate };
        }
      }
    }
    factors.value = Object.entries(grouped)
      .map(([name, v]) => ({
        name,
        yes: v.yes || { count: 0, rate: 0 },
        no: v.no || { count: 0, rate: 0 },
      }))
      .sort((a, b) => b.yes.rate - a.yes.rate); // 按风险率排序
  } catch {
    // keep empty
  } finally {
    loading.value = false;
  }
});

const riskRatio = (f: typeof factors.value[0]) => f.no.rate > 0 ? (f.yes.rate / f.no.rate).toFixed(1) : '-';

// Top 3 highest risk
const topRisk = computed(() => factors.value.slice(0, 3));
const totalFactors = computed(() => factors.value.length);
const highRiskCount = computed(() => factors.value.filter(f => f.yes.rate >= 0.1).length);

// Radar: only show factors with binary data (limit to top 8)
const radarFactors = computed(() => factors.value.filter(f => f.yes.count > 0 && f.no.count > 0).slice(0, 8));

const radarOption = computed(() => ({
  tooltip: {},
  radar: {
    indicator: radarFactors.value.map(f => ({ name: f.name, max: Math.max(...radarFactors.value.map(ff => ff.yes.rate)) * 1.3 || 0.3 })),
    shape: 'polygon',
    radius: '65%',
    splitArea: { areaStyle: { color: ['rgba(30,41,59,0.3)', 'rgba(15,23,42,0.3)'] } },
    axisName: { color: '#94a3b8', fontSize: 12 },
  },
  series: [{
    type: 'radar',
    data: [
      { value: radarFactors.value.map(f => f.yes.rate), name: '有该因素', lineStyle: { color: '#ef4444', width: 2 }, itemStyle: { color: '#ef4444' }, areaStyle: { color: 'rgba(239, 68, 68, 0.12)' } },
      { value: radarFactors.value.map(f => f.no.rate), name: '无该因素', lineStyle: { color: '#06b6d4', width: 2 }, itemStyle: { color: '#06b6d4' }, areaStyle: { color: 'rgba(6, 182, 212, 0.12)' } },
    ],
  }],
  legend: { bottom: 0, textStyle: { color: '#94a3b8' } },
}));

const compareOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 100, right: 40, top: 30, bottom: 50 },
  xAxis: { type: 'value', axisLabel: { color: '#94a3b8', formatter: '{value}%' }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } } },
  yAxis: { type: 'category', data: factors.value.map(f => f.name), axisLabel: { color: '#94a3b8', fontSize: 12 }, inverse: true },
  series: [
    { name: '有因素患病率', type: 'bar', data: factors.value.map(f => +(f.yes.rate * 100).toFixed(1)), itemStyle: { color: '#ef4444', borderRadius: [0, 4, 4, 0] }, barWidth: 14 },
    { name: '无因素患病率', type: 'bar', data: factors.value.map(f => +(f.no.rate * 100).toFixed(1)), itemStyle: { color: '#06b6d4', borderRadius: [0, 4, 4, 0] }, barWidth: 14 },
  ],
  legend: { bottom: 0, textStyle: { color: '#94a3b8' } },
}));

const columns: DataTableColumns = [
  { title: '因素', key: 'name', width: 120 },
  { title: '有因素人数', key: 'yesCount', width: 130, align: 'right', render: (row: any) => row.yes.count.toLocaleString() },
  {
    title: '有因素患病率', key: 'yesRate', width: 130, align: 'right',
    render: (row: any) => h('span', {
      style: { color: row.yes.rate >= 0.15 ? '#ef4444' : row.yes.rate >= 0.1 ? '#f59e0b' : '#22c55e', fontWeight: 600 }
    }, (row.yes.rate * 100).toFixed(1) + '%'),
  },
  { title: '无因素人数', key: 'noCount', width: 130, align: 'right', render: (row: any) => row.no.count.toLocaleString() },
  { title: '无因素患病率', key: 'noRate', width: 130, align: 'right', render: (row: any) => (row.no.rate * 100).toFixed(1) + '%' },
  {
    title: '风险倍率', key: 'ratio', width: 110, align: 'right',
    render: (row: any) => h(NTag, {
      size: 'small',
      type: row.no.rate > 0 && row.yes.rate / row.no.rate >= 2 ? 'error' : 'warning',
      bordered: false,
    }, { default: () => 'x' + riskRatio(row) }),
  },
];
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical :size="20">
      <!-- Top KPIs: only 4 cards, not all factors -->
      <n-grid :cols="4" :x-gap="16">
        <n-grid-item>
          <n-card>
            <n-statistic label="分析因素" :value="totalFactors" tabular-nums>
              <template #suffix><span style="font-size: 14px; color: #06b6d4;"> 个</span></template>
            </n-statistic>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="高风险因素" tabular-nums>
              <template #default><span style="color: #ef4444;">{{ highRiskCount }}</span></template>
              <template #suffix><span style="font-size: 14px; color: #ef4444;"> 个</span></template>
            </n-statistic>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="最高风险因素" tabular-nums>
              <template #default>
                <span style="color: #ef4444;">{{ topRisk[0]?.name || '-' }}</span>
              </template>
              <template #suffix>
                <n-tag v-if="topRisk[0]" type="error" size="small" :bordered="false">{{ (topRisk[0].yes.rate * 100).toFixed(1) }}%</n-tag>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="最大风险倍率" tabular-nums>
              <template #default>
                <span style="color: #f59e0b;">x{{ topRisk[0] ? riskRatio(topRisk[0]) : '-' }}</span>
              </template>
              <template #suffix>
                <span style="font-size: 13px; color: #94a3b8;">{{ topRisk[0]?.name || '' }}</span>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Charts: radar + comparison bar -->
      <n-grid :cols="5" :x-gap="16">
        <n-grid-item :span="2">
          <n-card title="风险因素雷达图">
            <EChart :option="radarOption" height="420px" />
          </n-card>
        </n-grid-item>
        <n-grid-item :span="3">
          <n-card title="有/无因素患病率对比">
            <EChart :option="compareOption" :height="Math.max(420, factors.length * 40 + 80) + 'px'" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Full data table -->
      <n-card title="全部因素详细数据">
        <n-data-table :columns="columns" :data="factors" :bordered="false" striped />
      </n-card>
    </n-space>
  </n-spin>
</template>
