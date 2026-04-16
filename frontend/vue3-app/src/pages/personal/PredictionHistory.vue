<script setup lang="ts">
import { ref, h, onMounted } from 'vue';
import { NCard, NSpace, NDataTable, NTag, NEmpty, NSpin } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import { requestJson } from '@/services/http';

interface PredictionRecord {
  id: number;
  probability: number;
  riskLevel: string;
  riskLabel: string;
  modelName: string;
  createdAt: string;
  inputData: any;
}

const records = ref<PredictionRecord[]>([]);
const total = ref(0);
const loading = ref(true);

const riskTagType = (level: string) => {
  if (level === 'high') return 'error';
  if (level === 'medium') return 'warning';
  return 'success';
};

const probColor = (prob: number) => {
  if (prob >= 0.7) return '#ef4444';
  if (prob >= 0.4) return '#f59e0b';
  return '#22c55e';
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const columns: DataTableColumns<PredictionRecord> = [
  {
    title: '时间',
    key: 'createdAt',
    width: 180,
    render(row) {
      return formatDate(row.createdAt);
    },
  },
  { title: '模型', key: 'modelName', width: 160 },
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
    key: 'riskLevel',
    width: 120,
    render(row) {
      return h(NTag, { type: riskTagType(row.riskLevel), size: 'small', bordered: false }, () => row.riskLabel);
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
