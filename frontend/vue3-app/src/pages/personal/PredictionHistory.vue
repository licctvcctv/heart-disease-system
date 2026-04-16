<script setup lang="ts">
import { ref, h, onMounted } from 'vue';
import { NCard, NSpace, NDataTable, NTag, NEmpty, NSpin } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import { requestJson } from '@/services/http';

interface PredictionRecord {
  id: number;
  probability: number;
  risk_level: number;
  risk_label: string;
  model_name: string;
  created_at: string;
  input_data: any;
}

const records = ref<PredictionRecord[]>([]);
const total = ref(0);
const loading = ref(true);

const riskTagType = (level: number) => {
  if (level >= 3) return 'error';
  if (level >= 2) return 'warning';
  return 'success';
};

const probColor = (prob: number) => {
  if (prob >= 0.7) return '#ef4444';
  if (prob >= 0.4) return '#f59e0b';
  return '#22c55e';
};

const columns: DataTableColumns<PredictionRecord> = [
  { title: '时间', key: 'created_at', width: 180 },
  { title: '模型', key: 'model_name', width: 160 },
  {
    title: '预测概率',
    key: 'probability',
    width: 120,
    render(row) {
      const val = (row.probability * 100).toFixed(1) + '%';
      return h('span', { style: { color: probColor(row.probability), fontWeight: 600 } }, val);
    },
  },
  {
    title: '风险等级',
    key: 'risk_level',
    width: 120,
    render(row) {
      return h(NTag, { type: riskTagType(row.risk_level), size: 'small', bordered: false }, () => row.risk_label || `等级${row.risk_level}`);
    },
  },
];

onMounted(async () => {
  try {
    const res = await requestJson<any>('/system/predictions');
    const data = res.data || res;
    records.value = data.records || [];
    total.value = data.total || records.value.length;
  } catch {
    // silently fail
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <n-space vertical :size="24">
    <n-card title="预测记录">
      <template #header-extra>
        <span style="font-size: 13px; color: #94a3b8;">共 {{ total }} 条记录</span>
      </template>

      <n-spin :show="loading">
        <n-data-table
          v-if="records.length > 0"
          :columns="columns"
          :data="records"
          :bordered="false"
          size="small"
        />
        <n-empty
          v-else-if="!loading"
          description="暂无预测记录，请在「风险预测」页面进行预测"
        />
      </n-spin>
    </n-card>
  </n-space>
</template>
