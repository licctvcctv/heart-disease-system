<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NStatistic, NDataTable, NTag, NSpace, NSpin, NEmpty } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

interface DatasetInfo {
  name: string;
  file: string;
  rows: number;
  cols: number;
  size: string;
  nulls: number;
  target: string;
  status: string;
}

const datasets = ref<DatasetInfo[]>([]);
const loading = ref(true);
const error = ref(false);

const totalRows = computed(() => datasets.value.reduce((s, d) => s + d.rows, 0));
const totalStorage = computed(() => {
  let bytes = 0;
  for (const d of datasets.value) {
    const s = d.size || '';
    const num = parseFloat(s);
    if (s.includes('MB')) bytes += num * 1024 * 1024;
    else if (s.includes('KB')) bytes += num * 1024;
    else if (s.includes('GB')) bytes += num * 1024 * 1024 * 1024;
  }
  if (bytes >= 1024 * 1024 * 1024) return (bytes / 1024 / 1024 / 1024).toFixed(1) + ' GB';
  if (bytes >= 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB';
  return (bytes / 1024).toFixed(1) + ' KB';
});
const qualityScore = computed(() => {
  if (datasets.value.length === 0) return '0';
  const total = datasets.value.reduce((s, d) => s + d.rows, 0);
  const nulls = datasets.value.reduce((s, d) => s + d.nulls, 0);
  return ((1 - nulls / total) * 100).toFixed(1);
});

const sizeOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    data: datasets.value.map((d, i) => ({
      value: d.rows,
      name: d.name,
      itemStyle: { color: ['#06b6d4', '#3b82f6', '#8b5cf6', '#f59e0b', '#22c55e'][i % 5] },
    })),
    label: { color: '#94a3b8', formatter: '{b}\n{d}%', fontSize: 10 },
  }],
}));

const colsOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 120, right: 40, top: 10, bottom: 10 },
  xAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } } },
  yAxis: { type: 'category', data: datasets.value.map(d => d.name), axisLabel: { color: '#94a3b8' } },
  series: [{
    type: 'bar',
    data: datasets.value.map((d, i) => ({ value: d.cols, itemStyle: { color: ['#06b6d4', '#3b82f6', '#8b5cf6', '#f59e0b', '#22c55e'][i % 5], borderRadius: [0, 4, 4, 0] } })),
    barWidth: 20,
    label: { show: true, position: 'right', color: '#94a3b8' },
  }],
}));

const columns: DataTableColumns = [
  { title: '名称', key: 'name', width: 160, render: (row: any) => h('span', { style: { fontWeight: 600 } }, row.name) },
  { title: '文件名', key: 'file', width: 200, render: (row: any) => h('span', { style: { fontFamily: 'monospace', fontSize: '12px' } }, row.file) },
  { title: '行数', key: 'rows', width: 120, align: 'right', render: (row: any) => row.rows.toLocaleString() },
  { title: '列数', key: 'cols', width: 80, align: 'right' },
  { title: '大小', key: 'size', width: 100, align: 'right' },
  {
    title: '缺失值',
    key: 'nulls',
    width: 100,
    align: 'right',
    render: (row: any) => h('span', {
      style: { color: row.nulls > 0 ? '#f59e0b' : '#22c55e', fontFamily: 'monospace' },
    }, row.nulls.toLocaleString()),
  },
  { title: '目标列', key: 'target', width: 140, render: (row: any) => h('span', { style: { fontFamily: 'monospace', fontSize: '12px' } }, row.target) },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render: (row: any) => h(NTag, {
      size: 'small',
      type: row.status === 'loaded' ? 'success' : 'warning',
      bordered: false,
    }, { default: () => row.status === 'loaded' ? '已加载' : '清洗中' }),
  },
];

onMounted(async () => {
  try {
    const res = await requestJson<any>('/dashboard/overview');
    const raw = res.datasets || res.data?.datasets || [];
    datasets.value = raw.map((d: any) => ({
      name: d.name || d.dataset_name || '',
      file: d.file || d.file_name || '',
      rows: d.rows || d.row_count || d.sample_count || 0,
      cols: d.cols || d.column_count || d.features || 0,
      size: d.size || d.file_size || '',
      nulls: d.nulls || d.null_count || 0,
      target: d.target || d.target_column || '',
      status: d.status || 'loaded',
    }));
  } catch {
    error.value = true;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <n-space vertical :size="24">
    <n-spin :show="loading">
      <template v-if="!loading && error">
        <n-card>
          <n-empty description="无法加载数据集信息，请检查后端服务是否启动" />
        </n-card>
      </template>

      <template v-else-if="!loading && datasets.length === 0">
        <n-card>
          <n-empty description="暂无数据集信息" />
        </n-card>
      </template>

      <template v-else-if="!loading">
        <!-- KPI Cards -->
        <n-grid :cols="4" :x-gap="16" :y-gap="16">
          <n-grid-item>
            <n-card>
              <n-statistic label="数据集总数" :value="datasets.length" tabular-nums>
                <template #suffix>
                  <span style="font-size: 14px; color: #06b6d4;"> 个</span>
                </template>
              </n-statistic>
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card>
              <n-statistic label="总记录数" tabular-nums>
                <template #default>
                  <span style="color: #3b82f6;">{{ (totalRows / 10000).toFixed(1) }}万</span>
                </template>
                <template #suffix>
                  <span style="font-size: 12px; color: #94a3b8;"> ({{ totalRows.toLocaleString() }} 行)</span>
                </template>
              </n-statistic>
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card>
              <n-statistic label="总存储空间" tabular-nums>
                <template #default>
                  <span style="color: #8b5cf6;">{{ totalStorage }}</span>
                </template>
                <template #suffix>
                  <span style="font-size: 12px; color: #94a3b8;"> CSV 原始文件</span>
                </template>
              </n-statistic>
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card>
              <n-statistic label="数据质量" tabular-nums>
                <template #default>
                  <span style="color: #22c55e;">{{ qualityScore }}%</span>
                </template>
                <template #suffix>
                  <span style="font-size: 12px; color: #94a3b8;"> 完整性评分</span>
                </template>
              </n-statistic>
            </n-card>
          </n-grid-item>
        </n-grid>

        <!-- Charts -->
        <n-grid :cols="2" :x-gap="16" style="margin-top: 24px;">
          <n-grid-item>
            <n-card title="样本量分布">
              <EChart :option="sizeOption" height="300px" />
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card title="特征维度对比">
              <EChart :option="colsOption" height="300px" />
            </n-card>
          </n-grid-item>
        </n-grid>

        <!-- Table -->
        <n-card title="数据集详情" style="margin-top: 24px;">
          <n-data-table :columns="columns" :data="datasets" :bordered="false" striped />
        </n-card>
      </template>
    </n-spin>
  </n-space>
</template>
