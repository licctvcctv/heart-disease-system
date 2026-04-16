<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { NCard, NGrid, NGridItem, NSpace, NStatistic, NTag, NSelect, NSpin } from 'naive-ui';
import EChart from '@/components/EChart.vue';
import { requestJson } from '@/services/http';

const loading = ref(true);

const features = ref<{ name: string; label: string; importance: number; category: string }[]>([]);

onMounted(async () => {
  try {
    const data = await requestJson<{ featureImportance: { feature: string; label: string; importance: number }[] }>('/model/metrics');
    const raw = data.featureImportance.sort((a, b) => b.importance - a.importance);
    const maxVal = raw.length > 0 ? raw[0].importance : 1;
    features.value = raw.map(f => ({
      name: f.feature,
      label: f.label,
      importance: maxVal > 0 ? f.importance / maxVal : 0, // normalize to 0-1
      category: categorize(f.feature),
    }));
  } catch {
    // API not available, keep empty
  } finally {
    loading.value = false;
  }
});

function categorize(feature: string): string {
  const map: Record<string, string> = {
    GenHealth: '健康状况', DiffWalking: '健康状况', PhysicalHealth: '健康状况', MentalHealth: '健康状况',
    BMI: '身体指标',
    AgeCategory: '人口学', Sex: '人口学', Race: '人口学',
    Diabetic: '疾病史', Stroke: '疾病史', KidneyDisease: '疾病史', Asthma: '疾病史', SkinCancer: '疾病史',
    Smoking: '生活方式', AlcoholDrinking: '生活方式', PhysicalActivity: '生活方式', SleepTime: '生活方式',
  };
  return map[feature] || '其他';
}

const barOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(51, 65, 85, 0.5)', textStyle: { color: '#e2e8f0' } },
  grid: { left: 120, right: 60, top: 10, bottom: 20 },
  xAxis: {
    type: 'value',
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)' } },
  },
  yAxis: {
    type: 'category',
    data: [...features.value].reverse().map(f => f.label),
    axisLabel: { color: '#64748b' },
  },
  series: [{
    type: 'bar',
    data: [...features.value].reverse().map(f => ({
      value: f.importance,
      itemStyle: {
        color: f.importance >= 0.1 ? '#ef4444' : f.importance >= 0.05 ? '#f59e0b' : '#06b6d4',
        borderRadius: [0, 4, 4, 0],
      },
    })),
    barWidth: 18,
    label: { show: true, position: 'right', color: '#64748b', fontSize: 11, formatter: (p: any) => (p.value * 100).toFixed(1) + '%' },
  }],
}));

const categoryColors: Record<string, string> = {
  '健康状况': '#06b6d4',
  '身体指标': '#3b82f6',
  '人口学': '#8b5cf6',
  '疾病史': '#ef4444',
  '生活方式': '#22c55e',
  '其他': '#94a3b8',
};

const categoryData = computed(() => {
  const groups: Record<string, number> = {};
  features.value.forEach(f => {
    groups[f.category] = (groups[f.category] || 0) + f.importance;
  });
  return Object.entries(groups).map(([name, value]) => ({ name, value: +value.toFixed(3) })).sort((a, b) => b.value - a.value);
});

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: (p: any) => `${p.name}<br/>重要性占比: ${(p.value * 100).toFixed(1)}%`, backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(51, 65, 85, 0.5)', textStyle: { color: '#e2e8f0' } },
  series: [{
    type: 'pie',
    radius: ['40%', '65%'],
    data: categoryData.value.map(d => ({
      value: d.value,
      name: d.name,
      itemStyle: { color: categoryColors[d.name] || '#94a3b8' },
    })),
    label: { color: '#64748b', formatter: '{b}\n{d}%' },
  }],
}));

const topN = ref(5);
const topFeatures = computed(() => features.value.slice(0, topN.value));

const topNOptions = [
  { label: 'Top 5', value: 5 },
  { label: 'Top 8', value: 8 },
  { label: 'Top 10', value: 10 },
  { label: '全部', value: 99 },
];

const rankColors = ['#f59e0b', '#94a3b8', '#cd7f32'];
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical :size="24">
      <!-- Top Features Ranking Cards -->
      <n-card title="特征重要性排名">
        <template #header-extra>
          <n-select v-model:value="topN" :options="topNOptions" size="small" style="width: 100px;" />
        </template>
        <n-grid :cols="5" :x-gap="12" :y-gap="12">
          <n-grid-item v-for="(f, i) in topFeatures" :key="f.name">
            <n-card size="small">
              <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span
                  style="width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700;"
                  :style="{
                    backgroundColor: i < 3 ? rankColors[i] + '22' : 'rgba(100,100,100,0.2)',
                    color: i < 3 ? rankColors[i] : '#999',
                  }"
                >{{ i + 1 }}</span>
                <n-tag size="tiny" :bordered="false" :color="{ color: (categoryColors[f.category] || '#94a3b8') + '15', textColor: categoryColors[f.category] || '#94a3b8' }">
                  {{ f.category }}
                </n-tag>
              </div>
              <n-statistic :label="f.label" tabular-nums>
                <template #default>{{ (f.importance * 100).toFixed(1) }}%</template>
              </n-statistic>
              <div style="margin-top: 8px; height: 6px; background: rgba(100,100,100,0.2); border-radius: 3px; overflow: hidden;">
                <div style="height: 100%; border-radius: 3px;" :style="{ width: (features[0] ? f.importance / features[0].importance * 100 : 0) + '%', backgroundColor: categoryColors[f.category] }" />
              </div>
            </n-card>
          </n-grid-item>
        </n-grid>
      </n-card>

      <!-- Charts -->
      <n-grid :cols="3" :x-gap="16">
        <n-grid-item :span="2">
          <n-card title="特征重要性排名 (CatBoost)">
            <EChart :option="barOption" height="500px" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="特征类别占比">
            <EChart :option="pieOption" height="300px" />
            <div style="margin-top: 16px;">
              <div v-for="d in categoryData" :key="d.name" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0;" :style="{ backgroundColor: categoryColors[d.name] }" />
                <span style="font-size: 12px; flex: 1;">{{ d.name }}</span>
                <span style="font-size: 12px; font-weight: 600;">{{ (d.value * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </n-space>
  </n-spin>
</template>
