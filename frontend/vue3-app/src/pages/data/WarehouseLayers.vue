<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue';
import { NCard, NGrid, NGridItem, NSpace, NTabs, NTabPane, NTag, NSpin, NDataTable } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

interface TableInfo {
  name: string;
  rows: number;
  description: string;
}

interface WarehouseData {
  ods: TableInfo[];
  dwd: TableInfo[];
  ads: TableInfo[];
}

const layers = ref<WarehouseData>({ ods: [], dwd: [], ads: [] });
const loading = ref(true);
const activeLayer = ref('ODS');

const columns: DataTableColumns<TableInfo> = [
  { title: '表名', key: 'name', width: 240 },
  { title: '行数', key: 'rows', width: 120 },
  { title: '描述', key: 'description' },
];

const tabConfig = [
  { key: 'ODS', label: 'ODS 原始数据层', color: '#06b6d4', dataKey: 'ods' as const },
  { key: 'DWD', label: 'DWD 明细数据层', color: '#3b82f6', dataKey: 'dwd' as const },
  { key: 'ADS', label: 'ADS 应用数据层', color: '#8b5cf6', dataKey: 'ads' as const },
];

const flowOption = computed(() => ({
  tooltip: {},
  series: [{
    type: 'sankey',
    layout: 'none',
    emphasis: { focus: 'adjacency' },
    data: [
      { name: 'CSV文件', itemStyle: { color: '#94a3b8' } },
      { name: 'ODS层', itemStyle: { color: '#06b6d4' } },
      { name: 'DWD层', itemStyle: { color: '#3b82f6' } },
      { name: 'ADS层', itemStyle: { color: '#8b5cf6' } },
      { name: 'MySQL', itemStyle: { color: '#22c55e' } },
      { name: 'Django API', itemStyle: { color: '#f59e0b' } },
    ],
    links: [
      { source: 'CSV文件', target: 'ODS层', value: 5 },
      { source: 'ODS层', target: 'DWD层', value: 5 },
      { source: 'DWD层', target: 'ADS层', value: 5 },
      { source: 'ADS层', target: 'MySQL', value: 5 },
      { source: 'MySQL', target: 'Django API', value: 5 },
    ],
    label: { color: '#94a3b8', fontSize: 12 },
    lineStyle: { color: 'gradient', curveness: 0.5 },
  }],
}));

onMounted(async () => {
  try {
    const res = await requestJson<any>('/system/warehouse');
    const data = res.layers || res.data?.layers || {};
    layers.value = {
      ods: data.ods || [],
      dwd: data.dwd || [],
      ads: data.ads || [],
    };
  } catch {
    // silently fail
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <n-space vertical :size="24">
    <!-- Layer Tabs with Data Tables -->
    <n-spin :show="loading">
      <n-tabs v-model:value="activeLayer" type="card" animated>
        <n-tab-pane v-for="tab in tabConfig" :key="tab.key" :name="tab.key">
          <template #tab>
            <n-space align="center" :size="8">
              <n-tag :color="{ color: tab.color, textColor: '#fff' }" size="small" :bordered="false">{{ tab.key }}</n-tag>
              <span>{{ tab.label }}</span>
            </n-space>
          </template>
          <n-card>
            <n-data-table
              :columns="columns"
              :data="layers[tab.dataKey]"
              :bordered="false"
              size="small"
              :pagination="false"
            />
          </n-card>
        </n-tab-pane>
      </n-tabs>
    </n-spin>

    <n-grid :cols="2" :x-gap="16">
      <!-- Data Flow -->
      <n-grid-item>
        <n-card title="数据流向">
          <EChart :option="flowOption" height="300px" />
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-space vertical :size="12">
          <n-card size="small" title="处理流程">
            <span style="font-size: 12px; color: #94a3b8; line-height: 1.6;">
              CSV → HDFS → Hive ODS (原始) → Hive DWD (清洗) → Hive ADS (聚合) → MySQL (导出) → Django API (服务)
            </span>
          </n-card>
          <n-card size="small" title="技术栈">
            <n-space :size="4">
              <n-tag size="small" type="info" :bordered="false">Hadoop HDFS</n-tag>
              <n-tag size="small" type="info" :bordered="false">Hive SQL</n-tag>
              <n-tag size="small" type="info" :bordered="false">Sqoop</n-tag>
              <n-tag size="small" type="info" :bordered="false">MySQL</n-tag>
              <n-tag size="small" type="info" :bordered="false">Django ORM</n-tag>
            </n-space>
          </n-card>
        </n-space>
      </n-grid-item>
    </n-grid>
  </n-space>
</template>
