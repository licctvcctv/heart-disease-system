<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NCard, NSpace, NTimeline, NTimelineItem, NTag, NSpin } from 'naive-ui';
import { requestJson } from '@/services/http';

interface EtlStep {
  step: number;
  name: string;
  source: string;
  target: string;
  method: string;
  status: string;
}

const steps = ref<EtlStep[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const res = await requestJson<any>('/system/etl-steps');
    steps.value = res.steps || res.data?.steps || [];
  } catch {
    // fallback empty
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <n-space vertical :size="24">
    <n-card title="数据清洗流程">
      <template #header-extra>
        <n-space :size="4">
          <n-tag size="small" type="info" :bordered="false">Hive SQL</n-tag>
          <n-tag size="small" type="info" :bordered="false">HDFS</n-tag>
          <n-tag size="small" type="info" :bordered="false">Sqoop</n-tag>
          <n-tag size="small" type="info" :bordered="false">MapReduce</n-tag>
        </n-space>
      </template>

      <n-spin :show="loading">
        <n-timeline v-if="steps.length > 0">
          <n-timeline-item
            v-for="s in steps"
            :key="s.step"
            :type="s.status === 'completed' ? 'success' : 'info'"
            :title="s.name"
          >
            <template #header>{{ s.name }}</template>
            {{ s.source }} → {{ s.target }}
            <br/>方法: {{ s.method }}
          </n-timeline-item>
        </n-timeline>
        <div v-else-if="!loading" style="color: #94a3b8; text-align: center; padding: 40px 0;">
          暂无 ETL 步骤数据
        </div>
      </n-spin>
    </n-card>
  </n-space>
</template>
