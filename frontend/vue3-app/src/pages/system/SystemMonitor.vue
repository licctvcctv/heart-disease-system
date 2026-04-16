<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NCard, NSpace, NGrid, NGridItem, NTag, NSpin } from 'naive-ui';
import { requestJson } from '@/services/http';

interface ServiceInfo {
  name: string;
  status: string;
  port: number;
}

interface JavaProcess {
  name: string;
  [key: string]: any;
}

const services = ref<ServiceInfo[]>([]);
const javaProcesses = ref<JavaProcess[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const res = await requestJson<any>('/system/cluster');
    const data = res.data || res;
    services.value = data.services || [];
    javaProcesses.value = data.javaProcesses || data.java_processes || [];
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
      <!-- Service Cards -->
      <n-card title="集群服务状态">
        <n-grid :cols="5" :x-gap="12" :y-gap="12">
          <n-grid-item v-for="s in services" :key="s.name">
            <n-card size="small" hoverable>
              <n-space vertical :size="8" align="center">
                <span style="font-size: 14px; font-weight: 600;">{{ s.name }}</span>
                <n-tag
                  :type="s.status === 'running' ? 'success' : 'error'"
                  size="small"
                  :bordered="false"
                >
                  {{ s.status === 'running' ? '运行中' : '已停止' }}
                </n-tag>
                <span style="font-size: 12px; color: #94a3b8;">端口: {{ s.port }}</span>
              </n-space>
            </n-card>
          </n-grid-item>
        </n-grid>
        <div v-if="!loading && services.length === 0" style="color: #94a3b8; text-align: center; padding: 24px 0;">
          暂无服务数据
        </div>
      </n-card>

      <!-- Java Processes -->
      <n-card title="Java 进程" style="margin-top: 16px;">
        <n-space :size="8" v-if="javaProcesses.length > 0">
          <n-tag
            v-for="(proc, idx) in javaProcesses"
            :key="idx"
            type="info"
            size="medium"
            :bordered="false"
          >
            {{ proc.name || proc }}
          </n-tag>
        </n-space>
        <div v-else-if="!loading" style="color: #94a3b8; text-align: center; padding: 24px 0;">
          暂无 Java 进程数据
        </div>
      </n-card>
    </n-spin>
  </n-space>
</template>
