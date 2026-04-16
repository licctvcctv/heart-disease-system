<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import EChart from '@/components/EChart.vue';
import ParticleBackground from '@/components/ParticleBackground.vue';
import StatTile from '@/components/StatTile.vue';
import { useDashboard } from '@/composables/useDashboard';
import type { ClinicalFeatureItem } from '@/types/dashboard';
import {
  createAgeOption,
  createClinicalOption,
  createImportanceBars,
  createLifestyleOption,
  createModelMetricsOption,
  createOverviewOption,
} from '@/utils/chartOptions';
import { formatCompact, formatInt, formatPercent, formatDateTime } from '@/utils/format';

const router = useRouter();
const { bundle, loading, error, now, refresh } = useDashboard();

const screenRef = ref<HTMLDivElement>();

const selectedClinicalFeature = ref('');

watch(
  () => bundle.value?.clinical.items,
  (items) => {
    if (!items || !items.length) return;
    if (!selectedClinicalFeature.value || !items.some((item) => item.feature === selectedClinicalFeature.value)) {
      selectedClinicalFeature.value = items[0].feature;
    }
  },
  { immediate: true },
);

const selectedClinical = computed<ClinicalFeatureItem | undefined>(() =>
  bundle.value?.clinical.items.find((item) => item.feature === selectedClinicalFeature.value),
);

const overviewOption = computed(() => createOverviewOption(bundle.value?.overview.prevalenceRate || 0));
const ageOption = computed(() => createAgeOption(bundle.value?.age.items || []));
// 大屏只显示患病率最高的前8个因素，避免拥挤
const topLifestyleItems = computed(() => {
  const items = bundle.value?.lifestyle.items || [];
  return [...items].sort((a, b) => b.prevalenceRate - a.prevalenceRate).slice(0, 8);
});
const lifestyleOption = computed(() => createLifestyleOption(topLifestyleItems.value));
const clinicalOption = computed(() => createClinicalOption(selectedClinical.value));
const metricsOption = computed(() => createModelMetricsOption(bundle.value?.metrics.models || []));
const importanceBars = computed(() => createImportanceBars(bundle.value?.metrics.featureImportance || []));

const goBack = () => router.push('/');

const updateScale = () => {
  const el = screenRef.value;
  if (!el) return;
  const scaleX = window.innerWidth / 1920;
  const scaleY = window.innerHeight / 1080;
  const scale = Math.min(scaleX, scaleY);
  el.style.transform = `scale(${scale})`;
};

onMounted(() => {
  document.body.classList.add('dark-body');
  updateScale();
  window.addEventListener('resize', updateScale);
});

onBeforeUnmount(() => {
  document.body.classList.remove('dark-body');
  window.removeEventListener('resize', updateScale);
});
</script>

<template>
  <div class="big-screen-wrapper">
    <ParticleBackground />
    <div class="grid-overlay" />
    <div class="scanline" />

    <div ref="screenRef" class="big-screen-container">
      <!-- ==================== HEADER ==================== -->
      <header class="screen-header">
        <!-- Left: status -->
        <div class="header-left">
          <button class="back-btn" title="返回管理后台" @click="goBack">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clip-rule="evenodd" />
            </svg>
          </button>
          <span class="status-badge" :class="loading ? 'status-loading' : 'status-ready'">
            <span class="status-dot" />
            {{ loading ? '数据加载中' : '数据就绪' }}
          </span>
        </div>

        <!-- Center: title -->
        <div class="header-center">
          <span class="title-line" />
          <span class="title-diamond" />
          <h1 class="header-title">心脏病健康数据分析大屏</h1>
          <span class="title-diamond" />
          <span class="title-line" />
        </div>

        <!-- Right: clock + refresh -->
        <div class="header-right">
          <div class="header-stats">
            <div class="stat-mini">
              <span class="stat-mini-label">样本</span>
              <span class="stat-mini-value">{{ formatInt(bundle?.overview.sampleCount || 0) }}</span>
            </div>
            <div class="stat-mini">
              <span class="stat-mini-label">患病率</span>
              <span class="stat-mini-value">{{ formatPercent(bundle?.overview.prevalenceRate || 0, 1) }}</span>
            </div>
            <div class="stat-mini">
              <span class="stat-mini-label">AUC</span>
              <span class="stat-mini-value">{{ (bundle?.overview.modelAuc || 0).toFixed(2) }}</span>
            </div>
          </div>
          <div class="header-clock">
            <div class="clock-time">{{ now.toLocaleTimeString('zh-CN', { hour12: false }) }}</div>
            <div class="clock-date">{{ formatDateTime(now) }}</div>
          </div>
          <button class="refresh-btn" @click="refresh">↻ 刷新</button>
        </div>
      </header>

      <!-- Error banner -->
      <div v-if="error" class="error-banner">{{ error }}</div>

      <!-- ==================== MAIN GRID ==================== -->
      <main class="screen-main">
        <!-- ========== LEFT COLUMN (25%) ========== -->
        <section class="col-left">
          <!-- KPI Stats -->
          <div class="screen-card kpi-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>总览指标</span>
              <span class="title-dots">
                <i class="pulse-dot" />
                <i class="pulse-dot d2" />
              </span>
            </div>
            <div class="kpi-grid">
              <StatTile label="样本总数" :value="formatCompact(bundle?.overview.sampleCount || 0)" hint="多数据集汇聚" tone="teal" />
              <StatTile label="阳性病例" :value="formatCompact(bundle?.overview.positiveCount || 0)" hint="高风险样本" tone="red" />
              <StatTile label="患病率" :value="formatPercent(bundle?.overview.prevalenceRate || 0, 1)" hint="总体基线" tone="amber" />
              <StatTile label="模型 AUC" :value="(bundle?.overview.modelAuc || 0).toFixed(2)" hint="当前最佳基线" tone="slate" />
            </div>
          </div>

          <!-- Overview donut -->
          <div class="screen-card flex-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>患病率概览</span>
            </div>
            <div class="chart-fill">
              <EChart :option="overviewOption" height="100%" />
            </div>
          </div>

          <!-- Lifestyle -->
          <div class="screen-card flex-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>生活方式分析</span>
            </div>
            <div class="chart-fill">
              <EChart :option="lifestyleOption" height="100%" />
            </div>
          </div>

          <!-- Datasets list -->
          <div class="screen-card dataset-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>数据集清单</span>
            </div>
            <div class="dataset-list">
              <div v-for="ds in bundle?.overview.datasets || []" :key="ds.name" class="dataset-item">
                <div class="dataset-name">{{ ds.name }}</div>
                <div class="dataset-meta">{{ formatInt(ds.rows) }} 行 · {{ ds.columns }} 列 · {{ ds.target }}</div>
                <div class="dataset-usage">{{ ds.usage }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- ========== CENTER COLUMN (50%) ========== -->
        <section class="col-center">
          <!-- Age bar chart (main) -->
          <div class="screen-card flex-card main-chart-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>年龄分层分析</span>
              <span class="card-subtitle">AGE DISTRIBUTION</span>
            </div>
            <div class="chart-fill">
              <EChart :option="ageOption" height="100%" />
            </div>
          </div>

          <!-- Clinical indicators -->
          <div class="screen-card flex-card">
            <div class="card-title-row">
              <div class="card-title" style="margin-bottom: 0;">
                <span class="title-dot" />
                <span>UCI 临床指标</span>
              </div>
              <div class="clinical-tabs">
                <button
                  v-for="item in bundle?.clinical.items || []"
                  :key="item.feature"
                  class="clinical-tab"
                  :class="{ active: selectedClinicalFeature === item.feature }"
                  @click="selectedClinicalFeature = item.feature"
                >
                  {{ item.label }}
                </button>
              </div>
            </div>
            <div class="chart-fill">
              <EChart :option="clinicalOption" height="100%" />
            </div>
          </div>
        </section>

        <!-- ========== RIGHT COLUMN (25%) ========== -->
        <section class="col-right">
          <!-- Model metrics -->
          <div class="screen-card flex-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>模型评估</span>
              <span class="card-subtitle">MODEL METRICS</span>
            </div>
            <div class="chart-area-sm">
              <EChart :option="metricsOption" height="100%" />
            </div>
          </div>

          <!-- Feature Importance -->
          <div class="screen-card flex-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>特征重要性排名</span>
            </div>
            <div class="importance-list">
              <div v-for="item in importanceBars" :key="item.label" class="importance-row">
                <span class="importance-label">{{ item.label }}</span>
                <div class="importance-track">
                  <div
                    class="importance-fill"
                    :class="{
                      'fill-high': item.tone === 'high',
                      'fill-medium': item.tone === 'medium',
                      'fill-low': item.tone === 'low',
                    }"
                    :style="{ width: item.width }"
                  />
                </div>
                <span class="importance-value">{{ item.value }}</span>
              </div>
            </div>
          </div>

          <!-- Comorbidity -->
          <div class="screen-card flex-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>共病概览</span>
            </div>
            <div class="comorbidity-list">
              <div v-for="slice in bundle?.derived.comorbidity || []" :key="slice.label" class="comorbidity-item">
                <div class="comorbidity-top">
                  <span class="comorbidity-name">{{ slice.label }}</span>
                  <span
                    class="comorbidity-val"
                    :class="{
                      'val-high': slice.tone === 'high',
                      'val-medium': slice.tone === 'medium',
                      'val-low': slice.tone === 'low',
                    }"
                  >{{ slice.value }}</span>
                </div>
                <div class="comorbidity-bottom">
                  <span>{{ formatInt(slice.sampleCount) }} 样本</span>
                  <span>{{ formatPercent(slice.prevalenceRate, 1) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Dataset info cards -->
          <div class="screen-card dataset-info-card">
            <div class="card-title">
              <span class="title-dot" />
              <span>数据集概要</span>
            </div>
            <div class="ds-info-grid">
              <div class="ds-info-item">
                <div class="ds-info-num">{{ formatInt(bundle?.overview.sampleCount || 0) }}</div>
                <div class="ds-info-lbl">总样本</div>
              </div>
              <div class="ds-info-item">
                <div class="ds-info-num">{{ bundle?.overview.datasets?.length || 0 }}</div>
                <div class="ds-info-lbl">数据集</div>
              </div>
              <div class="ds-info-item">
                <div class="ds-info-num">{{ formatInt(bundle?.overview.positiveCount || 0) }}</div>
                <div class="ds-info-lbl">阳性样本</div>
              </div>
              <div class="ds-info-item">
                <div class="ds-info-num">{{ (bundle?.overview.modelAuc || 0).toFixed(2) }}</div>
                <div class="ds-info-lbl">最佳AUC</div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* ===== WRAPPER ===== */
.big-screen-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #0a0e27;
  position: relative;
}

.big-screen-container {
  width: 1920px;
  height: 1080px;
  transform-origin: left top;
  position: absolute;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  color: #e2e8f0;
  font-family: 'Noto Sans SC', 'PingFang SC', system-ui, sans-serif;
}

/* ===== HEADER ===== */
.screen-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: linear-gradient(180deg, rgba(6, 30, 60, 0.9) 0%, rgba(10, 14, 39, 0.7) 100%);
  border-bottom: 1px solid rgba(6, 182, 212, 0.2);
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}

.screen-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.4), rgba(6, 182, 212, 0.6), rgba(6, 182, 212, 0.4), transparent);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 320px;
}

.back-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(100, 116, 139, 0.3);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}
.back-btn:hover {
  color: #06b6d4;
  border-color: rgba(6, 182, 212, 0.4);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}
.status-ready {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.08);
  border: 1px solid rgba(74, 222, 128, 0.2);
}
.status-loading {
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.2);
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: pulseDot 1.4s ease-in-out infinite;
}
.status-ready .status-dot { background: #4ade80; }
.status-loading .status-dot { background: #fbbf24; }

.header-center {
  display: flex;
  align-items: center;
  gap: 16px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.header-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 6px;
  background: linear-gradient(90deg, #67e8f9, #06b6d4, #67e8f9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

.title-line {
  display: block;
  width: 80px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.6));
}
.header-center .title-line:last-of-type {
  background: linear-gradient(90deg, rgba(6, 182, 212, 0.6), transparent);
}

.title-diamond {
  width: 8px;
  height: 8px;
  background: #06b6d4;
  transform: rotate(45deg);
  flex-shrink: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  width: 320px;
  justify-content: flex-end;
}

.header-stats {
  display: flex;
  gap: 16px;
}
.stat-mini {
  text-align: center;
  padding-right: 16px;
  border-right: 1px solid rgba(100, 116, 139, 0.15);
}
.stat-mini:last-child {
  border-right: none;
  padding-right: 0;
}
.stat-mini-label {
  display: block;
  font-size: 10px;
  color: #64748b;
}
.stat-mini-value {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: #e2e8f0;
  font-family: 'Courier New', monospace;
}

.header-clock {
  text-align: right;
}
.clock-time {
  font-size: 20px;
  font-weight: 600;
  color: #67e8f9;
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
}
.clock-date {
  font-size: 10px;
  color: #64748b;
}

.refresh-btn {
  padding: 5px 14px;
  border-radius: 6px;
  background: rgba(6, 182, 212, 0.12);
  border: 1px solid rgba(6, 182, 212, 0.25);
  color: #67e8f9;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.refresh-btn:hover {
  background: rgba(6, 182, 212, 0.2);
  border-color: rgba(6, 182, 212, 0.4);
}

/* ===== ERROR ===== */
.error-banner {
  margin: 8px 20px 0;
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 6px;
  color: #f87171;
  font-size: 13px;
  position: relative;
  z-index: 10;
}

/* ===== MAIN GRID ===== */
.screen-main {
  flex: 1;
  display: flex;
  gap: 10px;
  padding: 8px 16px 8px;
  min-height: 0;
  position: relative;
  z-index: 10;
}

.col-left {
  width: 25%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

.col-center {
  width: 50%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

.col-right {
  width: 25%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

/* ===== SCREEN CARD ===== */
.screen-card {
  position: relative;
  background: rgba(6, 30, 60, 0.6);
  border: 1px solid rgba(6, 182, 212, 0.15);
  border-radius: 4px;
  padding: 14px 16px;
  backdrop-filter: blur(8px);
}
.screen-card::before,
.screen-card::after {
  content: '';
  position: absolute;
  width: 12px;
  height: 12px;
  border-color: #06b6d4;
  border-style: solid;
  z-index: 1;
}
.screen-card::before {
  top: -1px;
  left: -1px;
  border-width: 2px 0 0 2px;
}
.screen-card::after {
  bottom: -1px;
  right: -1px;
  border-width: 0 2px 2px 0;
}

.flex-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

/* ===== CARD TITLE ===== */
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.title-dot {
  width: 4px;
  height: 14px;
  background: linear-gradient(180deg, #06b6d4, #0891b2);
  border-radius: 2px;
  flex-shrink: 0;
}

.title-dots {
  display: flex;
  gap: 4px;
  margin-left: auto;
}
.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #06b6d4;
  animation: pulseDot 1.4s ease-in-out infinite;
  display: block;
}
.pulse-dot.d2 {
  animation-delay: 0.2s;
}

.card-subtitle {
  margin-left: auto;
  font-size: 10px;
  font-weight: 400;
  color: rgba(6, 182, 212, 0.4);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  margin-bottom: 10px;
  gap: 12px;
}

/* ===== CHART AREAS ===== */
.chart-fill {
  flex: 1;
  min-height: 0;
}

.chart-area-sm {
  height: 180px;
  flex-shrink: 0;
}

/* ===== KPI ===== */
.kpi-card {
  flex-shrink: 0;
}
.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

/* ===== CLINICAL TABS ===== */
.clinical-tabs {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.clinical-tab {
  padding: 3px 10px;
  font-size: 11px;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
  background: transparent;
  border: 1px solid transparent;
}
.clinical-tab:hover {
  color: #94a3b8;
}
.clinical-tab.active {
  background: rgba(6, 182, 212, 0.15);
  color: #67e8f9;
  border-color: rgba(6, 182, 212, 0.3);
}

/* ===== IMPORTANCE ===== */
.importance-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.importance-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.importance-label {
  width: 80px;
  font-size: 11px;
  color: #94a3b8;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 0;
}
.importance-track {
  flex: 1;
  height: 10px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 5px;
  overflow: hidden;
}
.importance-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s ease;
}
.fill-high { background: linear-gradient(90deg, #ef4444, #f87171); }
.fill-medium { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.fill-low { background: linear-gradient(90deg, #14b8a6, #2dd4bf); }

.importance-value {
  width: 40px;
  font-size: 11px;
  color: #cbd5e1;
  font-family: 'Courier New', monospace;
  text-align: right;
  flex-shrink: 0;
}

/* ===== COMORBIDITY ===== */
.comorbidity-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.comorbidity-item {
  padding: 8px 10px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(51, 65, 85, 0.25);
  border-radius: 4px;
}
.comorbidity-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.comorbidity-name {
  font-size: 12px;
  color: #cbd5e1;
}
.comorbidity-val {
  font-size: 12px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
}
.val-high { color: #f87171; }
.val-medium { color: #fbbf24; }
.val-low { color: #2dd4bf; }
.comorbidity-bottom {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 10px;
  color: #64748b;
}

/* ===== DATASET LIST ===== */
.dataset-card {
  flex-shrink: 0;
}
.dataset-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.dataset-item {
  padding: 8px 10px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(51, 65, 85, 0.25);
  border-radius: 4px;
}
.dataset-name {
  font-size: 12px;
  font-weight: 500;
  color: #cbd5e1;
}
.dataset-meta {
  font-size: 10px;
  color: #64748b;
  margin-top: 2px;
}
.dataset-usage {
  font-size: 10px;
  color: rgba(6, 182, 212, 0.5);
  margin-top: 2px;
}

/* ===== DATASET INFO CARDS ===== */
.dataset-info-card {
  flex-shrink: 0;
}
.ds-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.ds-info-item {
  text-align: center;
  padding: 10px 8px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(51, 65, 85, 0.2);
  border-radius: 4px;
}
.ds-info-num {
  font-size: 18px;
  font-weight: 700;
  color: #67e8f9;
  font-family: 'Courier New', monospace;
}
.ds-info-lbl {
  font-size: 10px;
  color: #64748b;
  margin-top: 2px;
}

/* ===== MAIN CHART DECORATION ===== */
.main-chart-card {
  position: relative;
}
.main-chart-card::before {
  border-color: #22d3ee;
  border-width: 2px 0 0 2px;
  width: 16px;
  height: 16px;
}
.main-chart-card::after {
  border-color: #22d3ee;
  border-width: 0 2px 2px 0;
  width: 16px;
  height: 16px;
}
</style>
