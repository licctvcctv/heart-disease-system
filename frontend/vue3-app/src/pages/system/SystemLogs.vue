<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NCard, NSpace, NSpin, NTimeline, NTimelineItem, NTag, NGrid, NGridItem } from 'naive-ui';
import { requestJson } from '@/services/http';

interface ServiceInfo {
  name: string;
  status: string;
  host?: string;
  port?: number;
  [key: string]: any;
}

interface EtlStep {
  step: string;
  status: string;
  message?: string;
  timestamp?: string;
  duration?: number;
  [key: string]: any;
}

const loading = ref(true);
const services = ref<ServiceInfo[]>([]);
const etlSteps = ref<EtlStep[]>([]);

const statusTagType = (status: string) => {
  const s = status?.toLowerCase();
  if (s === 'running' || s === 'healthy' || s === 'ok' || s === 'success' || s === 'completed') return 'success';
  if (s === 'warning' || s === 'degraded') return 'warning';
  if (s === 'error' || s === 'failed' || s === 'down') return 'error';
  return 'info';
};

const etlTimelineType = (status: string): 'success' | 'warning' | 'error' | 'info' | 'default' => {
  const s = status?.toLowerCase();
  if (s === 'success' || s === 'completed' || s === 'done') return 'success';
  if (s === 'warning' || s === 'skipped') return 'warning';
  if (s === 'error' || s === 'failed') return 'error';
  return 'info';
};

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleString('zh-CN');
};

onMounted(async () => {
  try {
    const [clusterRes, etlRes] = await Promise.allSettled([
      requestJson<any>('/system/cluster'),
      requestJson<any>('/system/etl-steps'),
    ]);

    if (clusterRes.status === 'fulfilled') {
      const data = clusterRes.value.data || clusterRes.value;
      if (Array.isArray(data)) {
        services.value = data;
      } else if (data.services) {
        services.value = Array.isArray(data.services) ? data.services : Object.entries(data.services).map(([name, info]: [string, any]) => ({
          name,
          ...(typeof info === 'object' ? info : { status: String(info) }),
        }));
      } else {
        services.value = Object.entries(data).filter(([k]) => k !== 'timestamp' && k !== 'status').map(([name, info]: [string, any]) => ({
          name,
          ...(typeof info === 'object' ? info : { status: String(info) }),
        }));
      }
    }

    if (etlRes.status === 'fulfilled') {
      const data = etlRes.value.data || etlRes.value;
      etlSteps.value = Array.isArray(data) ? data : (data.steps || data.records || []);
    }
  } catch {
    // silently fail
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <n-space vertical :size="24">
    <n-spin :show="loading">
      <n-space vertical :size="24">
        <!-- Service Status -->
        <n-card title="服务运行状态">
          <template #header-extra>
            <span style="font-size: 13px; color: #94a3b8;">实时服务状态</span>
          </template>

          <n-grid v-if="services.length > 0" :cols="3" :x-gap="16" :y-gap="16">
            <n-grid-item v-for="(svc, idx) in services" :key="idx">
              <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
                <n-space justify="space-between" align="center">
                  <span style="font-weight: 600; font-size: 14px;">{{ svc.name }}</span>
                  <n-tag :type="statusTagType(svc.status)" size="small" :bordered="false">
                    {{ svc.status }}
                  </n-tag>
                </n-space>
                <div v-if="svc.host || svc.port" style="margin-top: 8px; font-size: 12px; color: #64748b;">
                  {{ svc.host }}{{ svc.port ? ':' + svc.port : '' }}
                </div>
              </div>
            </n-grid-item>
          </n-grid>
          <div v-else-if="!loading" style="color: #94a3b8; text-align: center; padding: 24px;">
            暂无服务状态信息
          </div>
        </n-card>

        <!-- ETL History -->
        <n-card title="ETL 执行记录">
          <template #header-extra>
            <span style="font-size: 13px; color: #94a3b8;">数据处理流水线执行历史</span>
          </template>

          <n-timeline v-if="etlSteps.length > 0">
            <n-timeline-item
              v-for="(step, idx) in etlSteps"
              :key="idx"
              :type="etlTimelineType(step.status)"
              :title="step.step || step.name || `步骤 ${idx + 1}`"
              :content="step.message || step.description || ''"
              :time="formatDate(step.timestamp) || (step.duration ? `耗时 ${step.duration}s` : '')"
            />
          </n-timeline>
          <div v-else-if="!loading" style="color: #94a3b8; text-align: center; padding: 24px;">
            暂无 ETL 执行记录
          </div>
        </n-card>
      </n-space>
    </n-spin>
  </n-space>
</template>
