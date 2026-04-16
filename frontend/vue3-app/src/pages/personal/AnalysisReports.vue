<script setup lang="ts">
import { NCard, NSpace, NResult } from 'naive-ui';
</script>

<template>
  <n-space vertical :size="24">
    <n-card title="分析报告">
      <n-result
        status="info"
        title="分析报告"
        description="报告功能开发中"
      />
    </n-card>
  </n-space>
</template>
