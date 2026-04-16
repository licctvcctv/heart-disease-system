<script setup lang="ts">
import type { DashboardOverview } from '@/types/dashboard';
import { formatDateTime, formatInt, formatPercent } from '@/utils/format';

defineProps<{
  overview: DashboardOverview | null;
  now: Date;
  loading: boolean;
}>();

const emit = defineEmits<{
  refresh: [];
}>();
</script>

<template>
  <header class="topbar">
    <div class="topbar__brand">
      <div class="topbar__mark">
        <span class="topbar__mark-line" />
        <span class="topbar__mark-text">HD</span>
      </div>
      <div>
        <div class="topbar__title">心脏病健康数据分析大屏</div>
        <div class="topbar__subtitle">Hive ADS · MySQL ADS · Kaggle / UCI 临床数据</div>
      </div>
    </div>

    <div class="topbar__meta">
      <div class="status-group">
        <span class="status-pill status-pill--teal" :class="{ 'is-muted': loading }">
          <i class="status-pill__dot" />
          {{ loading ? '读取 ADS' : '离线数据就绪' }}
        </span>
      </div>

      <div class="topbar__stats">
        <div class="topbar__stat">
          <span class="topbar__stat-label">样本</span>
          <strong>{{ formatInt(overview?.sampleCount || 0) }}</strong>
        </div>
        <div class="topbar__stat">
          <span class="topbar__stat-label">患病率</span>
          <strong>{{ formatPercent(overview?.prevalenceRate || 0, 1) }}</strong>
        </div>
        <div class="topbar__stat">
          <span class="topbar__stat-label">AUC</span>
          <strong>{{ (overview?.modelAuc || 0).toFixed(2) }}</strong>
        </div>
      </div>

      <div class="topbar__clock">
        <div class="topbar__clock-time">{{ now.toLocaleTimeString('zh-CN', { hour12: false }) }}</div>
        <div class="topbar__clock-date">{{ formatDateTime(now) }}</div>
      </div>

      <button class="refresh-btn" type="button" @click="emit('refresh')">
        <span class="refresh-btn__icon" aria-hidden="true">↻</span>
        刷新
      </button>
    </div>
  </header>
</template>
