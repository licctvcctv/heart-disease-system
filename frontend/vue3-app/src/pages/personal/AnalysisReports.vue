<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  NCard,
  NSpace,
  NSpin,
  NTag,
  NButton,
  NDescriptions,
  NDescriptionsItem,
  NStatistic,
  NGrid,
  NGridItem,
} from 'naive-ui';
import { requestJson } from '@/services/http';

interface Report {
  id: number;
  title: string;
  summary: string;
  date: string;
  type: string;
  expanded: boolean;
  data: Record<string, any>;
}

const loading = ref(true);
const reports = ref<Report[]>([]);

const today = new Date().toLocaleDateString('zh-CN');

const toggleExpand = (report: Report) => {
  report.expanded = !report.expanded;
};

onMounted(async () => {
  try {
    const [overviewRes, metricsRes] = await Promise.allSettled([
      requestJson<any>('/dashboard/overview'),
      requestJson<any>('/model/metrics'),
    ]);

    const generatedReports: Report[] = [];

    if (overviewRes.status === 'fulfilled') {
      const data = overviewRes.value.data || overviewRes.value;
      const sampleCount = data.totalSamples || data.total_samples || data.sampleCount || '-';
      const prevalence = data.prevalence ?? data.positive_rate ?? data.positiveRate;
      const datasets = data.datasets || data.datasetCount || data.dataset_count || '-';

      generatedReports.push({
        id: 1,
        title: '数据概览报告',
        summary: `当前系统共收录 ${sampleCount} 条样本数据，阳性率为 ${prevalence != null ? (prevalence * 100).toFixed(1) + '%' : '未知'}，涵盖 ${datasets} 个数据集。`,
        date: today,
        type: 'data',
        expanded: false,
        data: data,
      });
    }

    if (metricsRes.status === 'fulfilled') {
      const raw = metricsRes.value.data || metricsRes.value;
      const metricsList = Array.isArray(raw) ? raw : (raw.models || raw.metrics || [raw]);

      if (metricsList.length > 0) {
        const best = metricsList.reduce((a: any, b: any) => {
          const aAcc = a.accuracy ?? a.acc ?? 0;
          const bAcc = b.accuracy ?? b.acc ?? 0;
          return bAcc > aAcc ? b : a;
        }, metricsList[0]);

        const accuracy = best.accuracy ?? best.acc;
        const auc = best.auc ?? best.aucRoc ?? best.auc_roc;
        const modelName = best.modelName ?? best.model_name ?? best.name ?? '最优模型';

        generatedReports.push({
          id: 2,
          title: '模型评估报告',
          summary: `${modelName} 表现最优，准确率 ${accuracy != null ? (accuracy * 100).toFixed(1) + '%' : '未知'}，AUC 为 ${auc != null ? auc.toFixed(3) : '未知'}。共评估 ${metricsList.length} 个模型。`,
          date: today,
          type: 'model',
          expanded: false,
          data: { models: metricsList, best },
        });
      }
    }

    if (overviewRes.status === 'fulfilled' && metricsRes.status === 'fulfilled') {
      generatedReports.push({
        id: 3,
        title: '综合分析报告',
        summary: '基于数据概览与模型评估结果的综合分析，包含数据质量评估与模型性能对比。',
        date: today,
        type: 'comprehensive',
        expanded: false,
        data: {
          overview: overviewRes.value.data || overviewRes.value,
          metrics: metricsRes.value.data || metricsRes.value,
        },
      });
    }

    reports.value = generatedReports;
  } catch {
    // silently fail
  } finally {
    loading.value = false;
  }
});

const reportTagType = (type: string) => {
  if (type === 'data') return 'info';
  if (type === 'model') return 'success';
  return 'warning';
};

const reportTagLabel = (type: string) => {
  if (type === 'data') return '数据';
  if (type === 'model') return '模型';
  return '综合';
};
</script>

<template>
  <n-space vertical :size="24">
    <n-spin :show="loading">
      <n-space vertical :size="16">
        <div v-if="reports.length === 0 && !loading" style="text-align: center; color: #94a3b8; padding: 48px 0;">
          暂无可用报告数据
        </div>

        <n-card
          v-for="report in reports"
          :key="report.id"
          hoverable
          style="cursor: pointer;"
        >
          <n-space vertical :size="12">
            <!-- Header -->
            <n-space justify="space-between" align="center">
              <n-space align="center" :size="12">
                <span style="font-size: 16px; font-weight: 700;">{{ report.title }}</span>
                <n-tag :type="reportTagType(report.type)" size="small" :bordered="false">
                  {{ reportTagLabel(report.type) }}
                </n-tag>
              </n-space>
              <span style="font-size: 12px; color: #94a3b8;">{{ report.date }}</span>
            </n-space>

            <!-- Summary -->
            <p style="margin: 0; color: #64748b; font-size: 14px; line-height: 1.6;">
              {{ report.summary }}
            </p>

            <!-- Stats preview for data report -->
            <n-grid v-if="report.type === 'data' && !report.expanded" :cols="3" :x-gap="16">
              <n-grid-item>
                <n-statistic label="样本数" :value="report.data.totalSamples || report.data.total_samples || report.data.sampleCount || '-'" />
              </n-grid-item>
              <n-grid-item>
                <n-statistic label="阳性率">
                  <template #default>
                    {{ report.data.prevalence != null ? (report.data.prevalence * 100).toFixed(1) + '%' : (report.data.positive_rate != null ? (report.data.positive_rate * 100).toFixed(1) + '%' : '-') }}
                  </template>
                </n-statistic>
              </n-grid-item>
              <n-grid-item>
                <n-statistic label="数据集数" :value="report.data.datasets || report.data.datasetCount || report.data.dataset_count || '-'" />
              </n-grid-item>
            </n-grid>

            <!-- Expand button -->
            <n-space justify="end">
              <n-button text type="primary" @click="toggleExpand(report)">
                {{ report.expanded ? '收起详情' : '查看详情' }}
              </n-button>
            </n-space>

            <!-- Expanded details -->
            <div v-if="report.expanded" style="border-top: 1px solid #e2e8f0; padding-top: 16px;">
              <!-- Data report details -->
              <n-descriptions v-if="report.type === 'data'" bordered :column="2" label-placement="left">
                <n-descriptions-item v-for="(val, key) in report.data" :key="String(key)" :label="String(key)">
                  {{ typeof val === 'object' ? JSON.stringify(val) : val }}
                </n-descriptions-item>
              </n-descriptions>

              <!-- Model report details -->
              <template v-if="report.type === 'model'">
                <n-descriptions v-if="report.data.best" bordered :column="2" label-placement="left" style="margin-bottom: 16px;">
                  <n-descriptions-item label="最优模型">
                    {{ report.data.best.modelName || report.data.best.model_name || report.data.best.name || '-' }}
                  </n-descriptions-item>
                  <n-descriptions-item label="准确率">
                    {{ report.data.best.accuracy != null ? (report.data.best.accuracy * 100).toFixed(1) + '%' : '-' }}
                  </n-descriptions-item>
                  <n-descriptions-item label="AUC">
                    {{ report.data.best.auc != null ? report.data.best.auc.toFixed(3) : (report.data.best.aucRoc != null ? report.data.best.aucRoc.toFixed(3) : '-') }}
                  </n-descriptions-item>
                  <n-descriptions-item label="评估模型数">
                    {{ report.data.models?.length || '-' }}
                  </n-descriptions-item>
                </n-descriptions>
              </template>

              <!-- Comprehensive report details -->
              <template v-if="report.type === 'comprehensive'">
                <n-descriptions bordered :column="2" label-placement="left">
                  <n-descriptions-item v-for="(val, key) in report.data.overview" :key="'ov-' + String(key)" :label="'[数据] ' + String(key)">
                    {{ typeof val === 'object' ? JSON.stringify(val) : val }}
                  </n-descriptions-item>
                </n-descriptions>
              </template>
            </div>
          </n-space>
        </n-card>
      </n-space>
    </n-spin>
  </n-space>
</template>
