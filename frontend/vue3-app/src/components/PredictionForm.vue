<script setup lang="ts">
import { NForm, NFormItem, NGrid, NGridItem, NSelect, NInputNumber, NButton, NDivider } from 'naive-ui';
import type { PredictionFormModel } from '@/types/dashboard';

type FieldType = 'number' | 'select';

interface FieldConfig {
  key: keyof PredictionFormModel;
  label: string;
  type: FieldType;
  options?: Array<{ label: string; value: string }>;
  step?: number;
  min?: number;
  max?: number;
}

type NumericKey = 'BMI' | 'PhysicalHealth' | 'MentalHealth' | 'SleepTime';

const props = defineProps<{
  modelValue: PredictionFormModel;
  busy: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: PredictionFormModel];
  submit: [];
}>();

const binaryOptions = [
  { label: '是', value: 'Yes' },
  { label: '否', value: 'No' },
];

const numericFields: NumericKey[] = ['BMI', 'PhysicalHealth', 'MentalHealth', 'SleepTime'];

const fields: FieldConfig[] = [
  { key: 'BMI', label: 'BMI', type: 'number', step: 0.1, min: 10, max: 60 },
  { key: 'Smoking', label: '吸烟', type: 'select', options: binaryOptions },
  { key: 'AlcoholDrinking', label: '饮酒', type: 'select', options: binaryOptions },
  { key: 'Stroke', label: '卒中史', type: 'select', options: binaryOptions },
  { key: 'PhysicalHealth', label: '身体不适天数', type: 'number', min: 0, max: 30 },
  { key: 'MentalHealth', label: '心理不适天数', type: 'number', min: 0, max: 30 },
  { key: 'DiffWalking', label: '行走困难', type: 'select', options: binaryOptions },
  {
    key: 'Sex',
    label: '性别',
    type: 'select',
    options: [
      { label: '男', value: 'Male' },
      { label: '女', value: 'Female' },
    ],
  },
  {
    key: 'AgeCategory',
    label: '年龄段',
    type: 'select',
    options: ['18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80 or older'].map((value) => ({
      label: value,
      value,
    })),
  },
  {
    key: 'Diabetic',
    label: '糖尿病',
    type: 'select',
    options: [
      { label: '否', value: 'No' },
      { label: '是', value: 'Yes' },
      { label: '边缘', value: 'Borderline' },
      { label: '妊娠期', value: 'During pregnancy' },
    ],
  },
  { key: 'PhysicalActivity', label: '有运动', type: 'select', options: binaryOptions },
  {
    key: 'GenHealth',
    label: '总体健康',
    type: 'select',
    options: ['Poor', 'Fair', 'Good', 'Very good', 'Excellent'].map((value) => ({
      label: value,
      value,
    })),
  },
  { key: 'SleepTime', label: '睡眠时长', type: 'number', min: 1, max: 16 },
  { key: 'Asthma', label: '哮喘', type: 'select', options: binaryOptions },
  { key: 'KidneyDisease', label: '肾病', type: 'select', options: binaryOptions },
  { key: 'SkinCancer', label: '皮肤癌', type: 'select', options: binaryOptions },
];

const updateField = (key: keyof PredictionFormModel, rawValue: string | number | null) => {
  const next = { ...props.modelValue } as Record<keyof PredictionFormModel, string | number>;
  if (numericFields.includes(key as NumericKey)) {
    next[key] = rawValue == null ? 0 : Number(rawValue);
  } else {
    next[key] = rawValue as string;
  }
  emit('update:modelValue', next as PredictionFormModel);
};
</script>

<template>
  <n-form label-placement="top">
    <n-grid :cols="2" :x-gap="16" :y-gap="4">
      <n-grid-item v-for="field in fields" :key="field.key">
        <n-form-item :label="field.label">
          <n-select
            v-if="field.type === 'select'"
            :value="String(modelValue[field.key])"
            :options="field.options || []"
            @update:value="(val: string) => updateField(field.key, val)"
          />
          <n-input-number
            v-else
            :value="Number(modelValue[field.key])"
            :step="field.step"
            :min="field.min"
            :max="field.max"
            style="width: 100%"
            @update:value="(val: number | null) => updateField(field.key, val)"
          />
        </n-form-item>
      </n-grid-item>
    </n-grid>

    <n-divider />

    <div style="display: flex; align-items: center; justify-content: space-between;">
      <span style="font-size: 12px; opacity: 0.5;">模型输入 16 项</span>
      <n-button type="primary" :loading="busy" @click="emit('submit')">执行预测</n-button>
    </div>
  </n-form>
</template>
