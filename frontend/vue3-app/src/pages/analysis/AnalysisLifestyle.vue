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
    // Group by factor: build yes/no structure
    const grouped: Record<string, { yes?: { count: number; rate: number }; no?: { count: number; rate: number } }> = {};
    for (const item of data.items) {
      if (!grouped[item.factor]) grouped[item.factor] = {};
      const cat = item.category.toLowerCase();
      if (cat === 'yes' || cat === '是') {
        grouped[item.factor].yes = { count: item.sampleCount, rate: item.prevalenceRate };
      } else if (cat === 'no' || cat === '否') {
        grouped[item.factor].no = { count: item.sampleCount, rate: item.prevalenceRate };
      } else {
        // For non-binary factors, treat first category as yes, second as no
        if (!grouped[item.factor].yes) {
          grouped[item.factor].yes = { count: item.sampleCount, rate: item.prevalenceRate };
        } else if (!grouped[item.factor].no) {
          grouped[item.factor].no = { count: item.sampleCount, rate: item.prevalenceRate };
        }
      }
    }
    factors.value = Object.entries(grouped).map(([name, v]) => ({
      name,
      yes: v.yes || { count: 0, rate: 0 },
      no: v.no || { count: 0, rate: 0 },
    }));
  } catch {
    // API not available, keep empty
  } finally {
    loading.value = false;
  }
});

const selectedFactor = computed(() => factors.value.length > 0 ? factors.value[0].name : '');
const selectedFactorRef = ref('');
const activeSelectedFactor = computed(() => {
  if (selectedFactorRef.value && factors.value.find(f => f.name === selectedFactorRef.value)) {
    return selectedFactorRef.value;
  }
  return factors.value.length > 0 ? factors.value[0].name : '';
});
const currentFactor = computed(() => factors.value.find(f => f.name === activeSelectedFactor.value) || { name: '', yes: { count: 0, rate: 0 }, no: { count: 0, rate: 0 } });

const radarOption = computed(() => ({
  tooltip: {},
  radar: {
    indicator: factors.value.map(f => ({ name: f.name, max: 0.35 })),
    shape: 'polygon',
    splitArea: { areaStyle: { color: ['rgba(30,41,59,0.3)', 'rgba(15,23,42,0.3)'] } },
    axisName: { color: '#64748b', fontSize: 11 },
  },
  series: [{
    type: 'radar',
    data: [
      {
        value: factors.value.map(f => f.yes.rate),
        name: '有该因素',
        lineStyle: { color: '#ef4444' },
        itemStyle: { color: '#ef4444' },
        areaStyle: { color: 'rgba(239, 68, 68, 0.1)' },
      },
      {
        value: factors.value.map(f => f.no.rate),
        name: '无该因素',
        lineStyle: { color: '#06b6d4' },
        itemStyle: { color: '#06b6d4' },
        areaStyle: { color: 'rgba(6, 182, 212, 0.1)' },
      },
    ],
  }],
  legend: { bottom: 0, textStyle: { color: '#64748b' } },
}));

const compareOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 80, right: 30, top: 20, bottom: 40 },
  xAxis: { type: 'value', axisLabel: { color: '#64748b', formatter: '{value}%' }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } } },
  yAxis: { type: 'category', data: factors.value.map(f => f.name), axisLabel: { color: '#64748b' } },
  series: [
    {
      name: '有因素患病率',
      type: 'bar',
      data: factors.value.map(f => +(f.yes.rate * 100).toFixed(1)),
      itemStyle: { color: '#ef4444', borderRadius: [0, 4, 4, 0] },
      barWidth: 12,
    },
    {
      name: '无因素患病率',
      type: 'bar',
      data: factors.value.map(f => +(f.no.rate * 100).toFixed(1)),
      itemStyle: { color: '#06b6d4', borderRadius: [0, 4, 4, 0] },
      barWidth: 12,
    },
  ],
  legend: { bottom: 0, textStyle: { color: '#64748b' } },
}));

const riskRatio = (f: typeof factors.value[0]) => f.no.rate > 0 ? (f.yes.rate / f.no.rate).toFixed(1) : '-';

const columns: DataTableColumns = [
  { title: '因素', key: 'name', width: 100 },
  { title: '有因素人数', key: 'yesCount', width: 120, align: 'right', render: (row: any) => row.yes.count.toLocaleString() },
  { title: '有因素患病率', key: 'yesRate', width: 120, align: 'right',
    render: (row: any) => h('span', {
      style: { color: row.yes.rate >= 0.15 ? '#ef4444' : row.yes.rate >= 0.1 ? '#f59e0b' : '#22c55e', fontWeight: 600 }
    }, (row.yes.rate * 100).toFixed(1) + '%'),
  },
  { title: '无因素人数', key: 'noCount', width: 120, align: 'right', render: (row: any) => row.no.count.toLocaleString() },
  { title: '无因素患病率', key: 'noRate', width: 120, align: 'right', render: (row: any) => (row.no.rate * 100).toFixed(1) + '%' },
  { title: '风险倍率', key: 'ratio', width: 100, align: 'right',
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
    <n-space vertical :size="24">
      <!-- KPI Cards -->
      <n-grid :cols="4" :x-gap="16" :y-gap="16">
        <n-grid-item v-for="f in factors" :key="f.name">
          <n-card
            :style="{
              cursor: 'pointer',
              borderColor: activeSelectedFactor === f.name ? 'rgba(6,182,212,0.5)' : undefined,
              boxShadow: activeSelectedFactor === f.name ? '0 0 0 2px rgba(6,182,212,0.2)' : undefined,
            }"
            @click="selectedFactorRef = f.name"
          >
            <n-statistic :label="f.name" tabular-nums>
              <template #default>
                <span :style="{ color: f.yes.rate >= 0.15 ? '#ef4444' : f.yes.rate >= 0.1 ? '#f59e0b' : undefined }">
                  {{ (f.yes.rate * 100).toFixed(1) }}%
                </span>
              </template>
              <template #suffix>
                <span style="font-size: 12px; color: #ef4444;">x{{ riskRatio(f) }}</span>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Charts -->
      <n-grid :cols="2" :x-gap="16">
        <n-grid-item>
          <n-card title="风险因素雷达图">
            <EChart :option="radarOption" height="380px" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="有/无因素患病率对比">
            <EChart :option="compareOption" height="380px" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- Detail panel -->
      <n-card v-if="currentFactor.name" :title="currentFactor.name + ' — 详细分析'">
        <n-grid :cols="3" :x-gap="16">
          <n-grid-item>
            <n-card style="background: rgba(239,68,68,0.05);">
              <n-statistic :label="'有' + currentFactor.name + '群体'" tabular-nums>
                <template #default>
                  <span style="color: #ef4444;">{{ currentFactor.yes.count.toLocaleString() }}</span>
                </template>
                <template #suffix>
                  <n-tag type="error" size="small" :bordered="false">患病率 {{ (currentFactor.yes.rate * 100).toFixed(1) }}%</n-tag>
                </template>
              </n-statistic>
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card style="background: rgba(6,182,212,0.05);">
              <n-statistic :label="'无' + currentFactor.name + '群体'" tabular-nums>
                <template #default>
                  <span style="color: #06b6d4;">{{ currentFactor.no.count.toLocaleString() }}</span>
                </template>
                <template #suffix>
                  <n-tag type="info" size="small" :bordered="false">患病率 {{ (currentFactor.no.rate * 100).toFixed(1) }}%</n-tag>
                </template>
              </n-statistic>
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card style="background: rgba(245,158,11,0.05);">
              <n-statistic label="风险倍率" tabular-nums>
                <template #default>
                  <span style="color: #f59e0b;">x{{ riskRatio(currentFactor) }}</span>
                </template>
                <template #suffix>
                  <span style="font-size: 14px; color: #f59e0b;">相对风险比</span>
                </template>
              </n-statistic>
            </n-card>
          </n-grid-item>
        </n-grid>
      </n-card>

      <!-- Table -->
      <n-card title="全部因素数据">
        <n-data-table :columns="columns" :data="factors" :bordered="false" striped />
      </n-card>
    </n-space>
  </n-spin>
</template>
