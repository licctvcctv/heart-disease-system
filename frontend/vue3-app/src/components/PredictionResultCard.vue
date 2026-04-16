<script setup lang="ts">
import { computed } from 'vue';
import { NCard, NTag, NStatistic, NDescriptions, NDescriptionsItem, NList, NListItem, NEmpty, NSpace } from 'naive-ui';
import type { PredictionResponse } from '@/types/dashboard';
import { formatDateTime, formatPercent } from '@/utils/format';

const props = defineProps<{
  result: PredictionResponse | null;
  busy: boolean;
}>();

const tagType = computed(() => {
  const level = props.result?.riskLevel;
  if (level === 'high') return 'error';
  if (level === 'medium') return 'warning';
  return 'success';
});

const statusLabel = computed(() => {
  if (props.result) return props.result.riskLabel;
  return props.busy ? '分析中' : '等待输入';
});
</script>

<template>
  <n-card title="预测结果">
    <template #header-extra>
      <n-tag :type="tagType" size="small" round>{{ statusLabel }}</n-tag>
    </template>

    <template v-if="result">
      <n-space vertical :size="16" align="center">
        <n-statistic label="心脏病预测概率" tabular-nums>
          <template #prefix />
          {{ formatPercent(result.probability, 1) }}
        </n-statistic>
      </n-space>

      <n-descriptions :column="2" bordered size="small" style="margin-top: 16px;">
        <n-descriptions-item label="模型">{{ result.model }}</n-descriptions-item>
        <n-descriptions-item label="时间">{{ formatDateTime(result.createdAt) }}</n-descriptions-item>
      </n-descriptions>

      <n-list bordered size="small" style="margin-top: 16px;">
        <n-list-item v-for="factor in result.topFactors" :key="factor.feature">
          <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <span>{{ factor.label }}</span>
            <strong style="font-family: monospace;">{{ factor.impact }}</strong>
          </div>
        </n-list-item>
      </n-list>
    </template>

    <n-empty v-else description="等待预测结果" style="padding: 32px 0;">
      <template #extra>
        <span style="font-size: 12px; opacity: 0.6;">等待模型返回风险概率、模型名称和主要贡献因子。</span>
      </template>
    </n-empty>
  </n-card>
</template>
