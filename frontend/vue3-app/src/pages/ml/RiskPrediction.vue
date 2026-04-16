<script setup lang="ts">
import { ref } from 'vue';
import { NCard, NGrid, NGridItem, NSpace, NButton, NTag, NList, NListItem, NEmpty, useMessage } from 'naive-ui';
import PredictionForm from '@/components/PredictionForm.vue';
import PredictionResultCard from '@/components/PredictionResultCard.vue';
import { predictHeartRisk } from '@/services/predictService';
import type { PredictionFormModel, PredictionResponse } from '@/types/dashboard';
import { createDefaultPredictionForm } from '@/types/dashboard';

let message: ReturnType<typeof useMessage> | null = null;
try { message = useMessage(); } catch { /* provider not ready */ }
const form = ref<PredictionFormModel>(createDefaultPredictionForm());
const prediction = ref<PredictionResponse | null>(null);
const predicting = ref(false);

const history = ref<{ time: string; risk: string; probability: number; model: string }[]>([]);

const handlePredict = async () => {
  predicting.value = true;
  try {
    prediction.value = await predictHeartRisk(form.value);
    if (prediction.value) {
      history.value.unshift({
        time: new Date().toLocaleString('zh-CN'),
        risk: prediction.value.riskLabel,
        probability: prediction.value.probability,
        model: prediction.value.model,
      });
      message?.success('预测完成');
    }
  } catch (e: any) {
    message?.error(e.message || '预测失败');
  } finally {
    predicting.value = false;
  }
};

const resetForm = () => {
  form.value = createDefaultPredictionForm();
  prediction.value = null;
};

const riskTagType = (risk: string) => risk === '高风险' ? 'error' : risk === '中风险' ? 'warning' : 'success';

const probColor = (p: number) => p >= 0.5 ? '#ef4444' : p >= 0.3 ? '#f59e0b' : '#22c55e';
</script>

<template>
  <n-space vertical :size="24">
    <n-grid :cols="5" :x-gap="20">
      <!-- Form -->
      <n-grid-item :span="3">
        <n-card title="健康指标录入">
          <template #header-extra>
            <n-button size="small" @click="resetForm">重置表单</n-button>
          </template>
          <PredictionForm v-model="form" :busy="predicting" @submit="handlePredict" />
        </n-card>
      </n-grid-item>

      <!-- Result & History & Info -->
      <n-grid-item :span="2">
        <n-space vertical :size="16">
          <PredictionResultCard :result="prediction" :busy="predicting" />

          <n-card title="预测历史">
            <template v-if="history.length === 0">
              <n-empty description="暂无预测记录，请填写表单进行预测" />
            </template>
            <n-list v-else bordered size="small">
              <n-list-item v-for="(h, i) in history" :key="i">
                <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
                  <n-tag size="small" :type="riskTagType(h.risk)" :bordered="false">{{ h.risk }}</n-tag>
                  <div style="flex: 1; min-width: 0;">
                    <div style="font-size: 11px; opacity: 0.5;">{{ h.time }}</div>
                  </div>
                  <div style="text-align: right;">
                    <div style="font-size: 14px; font-weight: 700; font-family: monospace;" :style="{ color: probColor(h.probability) }">
                      {{ (h.probability * 100).toFixed(1) }}%
                    </div>
                    <div style="font-size: 10px; opacity: 0.5;">{{ h.model }}</div>
                  </div>
                </div>
              </n-list-item>
            </n-list>
          </n-card>

          <n-card title="预测说明">
            <n-list size="small">
              <n-list-item>使用 CatBoost 模型，AUC 0.936</n-list-item>
              <n-list-item>基于 Kaggle 2020 数据集训练</n-list-item>
              <n-list-item>16 个健康指标综合评估</n-list-item>
              <n-list-item>结果仅供参考，不代替医学诊断</n-list-item>
            </n-list>
          </n-card>
        </n-space>
      </n-grid-item>
    </n-grid>
  </n-space>
</template>
