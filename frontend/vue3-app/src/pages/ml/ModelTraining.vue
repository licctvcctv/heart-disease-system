<script setup lang="ts">
import { ref, h, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NSpace, NForm, NFormItem, NSelect, NInputNumber, NCheckbox, NButton, NDataTable, NTag, NSpin } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import { requestJson } from '@/services/http';

const loading = ref(true);

const models = ref<{ name: string; status: string; accuracy: number; auc: number; trainTime: string; lastTrain: string; dataset: string; samples: number; epochs: number }[]>([]);

onMounted(async () => {
  try {
    const data = await requestJson<{ models: { name: string; accuracy: number; precision: number; recall: number; f1: number; auc: number }[] }>('/model/metrics');
    models.value = data.models.map(m => ({
      name: m.name,
      status: m.auc > 0 ? 'completed' : 'idle',
      accuracy: m.accuracy,
      auc: m.auc,
      trainTime: '-',
      lastTrain: '-',
      dataset: '-',
      samples: 0,
      epochs: 0,
    }));
  } catch {
    // API not available, keep empty
  } finally {
    loading.value = false;
  }
});

const trainedCount = () => models.value.filter(m => m.status === 'completed').length;

const trainingConfig = ref({
  model: 'CatBoost',
  dataset: 'Kaggle 2020',
  testRatio: 0.2,
  crossValidation: 5,
  smote: true,
});

const isTraining = ref(false);

const startTraining = () => {
  isTraining.value = true;
  setTimeout(() => { isTraining.value = false; }, 3000);
};

const modelOptions = [
  { label: 'CatBoost', value: 'CatBoost' },
  { label: 'XGBoost', value: 'XGBoost' },
  { label: 'Logistic Regression', value: 'Logistic Regression' },
  { label: 'Random Forest', value: 'Random Forest' },
  { label: 'SVM', value: 'SVM' },
];

const datasetOptions = [
  { label: 'Kaggle 2020', value: 'Kaggle 2020' },
  { label: 'Kaggle 2022', value: 'Kaggle 2022' },
  { label: 'UCI Cleveland', value: 'UCI Cleveland' },
];

const columns: DataTableColumns = [
  { title: '模型名称', key: 'name', width: 160 },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render: (row: any) => h(NTag, {
      size: 'small',
      type: row.status === 'completed' ? 'success' : row.status === 'training' ? 'info' : 'default',
      bordered: false,
    }, { default: () => row.status === 'completed' ? '已完成' : row.status === 'training' ? '训练中' : '未训练' }),
  },
  {
    title: 'Accuracy',
    key: 'accuracy',
    width: 100,
    align: 'right',
    render: (row: any) => row.accuracy > 0 ? row.accuracy.toFixed(3) : '-',
  },
  {
    title: 'AUC',
    key: 'auc',
    width: 100,
    align: 'right',
    render: (row: any) => h('span', {
      style: row.auc > 0 ? { color: '#22c55e', fontWeight: 600 } : {},
    }, row.auc > 0 ? row.auc.toFixed(3) : '-'),
  },
  { title: '训练耗时', key: 'trainTime', width: 100, align: 'right' },
  { title: '数据集', key: 'dataset', width: 120 },
  { title: '最近训练', key: 'lastTrain', width: 160, align: 'right' },
];
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical :size="24">
      <n-grid :cols="3" :x-gap="16">
        <!-- Training Config -->
        <n-grid-item>
          <n-card title="训练配置">
            <n-form label-placement="top" :show-feedback="false">
              <n-form-item label="选择模型">
                <n-select v-model:value="trainingConfig.model" :options="modelOptions" />
              </n-form-item>
              <n-form-item label="数据集">
                <n-select v-model:value="trainingConfig.dataset" :options="datasetOptions" />
              </n-form-item>
              <n-form-item label="测试集比例">
                <n-input-number v-model:value="trainingConfig.testRatio" :step="0.05" :min="0.1" :max="0.4" style="width: 100%" />
              </n-form-item>
              <n-form-item label="交叉验证折数">
                <n-input-number v-model:value="trainingConfig.crossValidation" :min="2" :max="10" style="width: 100%" />
              </n-form-item>
              <n-form-item>
                <n-checkbox v-model:checked="trainingConfig.smote">SMOTE 过采样</n-checkbox>
              </n-form-item>
              <n-form-item>
                <n-button type="primary" block :loading="isTraining" :disabled="isTraining" @click="startTraining">
                  {{ isTraining ? '训练中...' : '开始训练' }}
                </n-button>
              </n-form-item>
            </n-form>

            <n-card size="small" style="margin-top: 16px;" title="训练参数说明">
              <ul style="font-size: 13px; color: #999; padding-left: 0; list-style: none; margin: 0;">
                <li style="margin-bottom: 4px;">* SMOTE: 解决正负样本不均衡</li>
                <li style="margin-bottom: 4px;">* 交叉验证: 评估模型稳定性</li>
                <li>* 特征工程自动完成</li>
              </ul>
            </n-card>
          </n-card>
        </n-grid-item>

        <!-- Model List -->
        <n-grid-item :span="2">
          <n-card title="模型训练记录">
            <template #header-extra>
              <n-tag type="success" size="small" :bordered="false">{{ trainedCount() }} 个模型已训练</n-tag>
            </template>
            <n-data-table :columns="columns" :data="models" :bordered="false" striped />
          </n-card>
        </n-grid-item>
      </n-grid>
    </n-space>
  </n-spin>
</template>
