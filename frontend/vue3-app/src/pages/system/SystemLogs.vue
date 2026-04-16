<script setup lang="ts">
import { NCard, NSpace, NResult } from 'naive-ui';
</script>

<template>
  <n-space vertical :size="24">
    <n-card title="系统操作日志">
      <n-result
        status="info"
        title="系统日志"
        description="日志采集模块开发中"
      />
    </n-card>
  </n-space>
</template>
