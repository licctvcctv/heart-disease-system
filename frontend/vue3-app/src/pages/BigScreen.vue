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
const lifestyleOption = computed(() => createLifestyleOption(bundle.value?.lifestyle.items || []));
const clinicalOption = computed(() => createClinicalOption(selectedClinical.value));
const metricsOption = computed(() => createModelMetricsOption(bundle.value?.metrics.models || []));
const importanceBars = computed(() => createImportanceBars(bundle.value?.metrics.featureImportance || []));

const goBack = () => router.push('/');

onMounted(() => document.body.classList.add('dark-body'));
onBeforeUnmount(() => document.body.classList.remove('dark-body'));
</script>

<template>
  <div class="min-h-screen relative">
    <ParticleBackground />
    <div class="grid-overlay" />
    <div class="scanline" />

    <!-- Top Bar -->
    <header class="relative z-10 flex items-center justify-between border-b border-cyan-900/20" style="height: 4rem; padding: 0 1.5rem;">
      <div class="flex items-center gap-4">
        <button
          class="flex items-center justify-center rounded-lg bg-slate-800/60 border border-slate-700/50 text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30 transition-all"
          style="width: 2rem; height: 2rem;"
          title="返回管理后台"
          @click="goBack"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" style="width: 14px; height: 14px;">
            <path fill-rule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clip-rule="evenodd" />
          </svg>
        </button>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <span class="text-white font-bold text-xs">HD</span>
          </div>
          <div>
            <div class="font-bold text-slate-100" style="font-size: 18px; letter-spacing: 0.5px;">心脏病健康数据分析大屏</div>
            <div class="text-slate-500" style="font-size: 10px;">Hive ADS · MySQL ADS · Kaggle / UCI 临床数据</div>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-6">
        <span
          class="flex items-center gap-2 rounded-full text-xs border"
          style="padding: 4px 14px;"
          :class="loading ? 'text-amber-400 border-amber-500/30 bg-amber-500/10' : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'"
        >
          <span class="rounded-full" style="width: 6px; height: 6px; animation: pulseDot 1.4s ease-in-out infinite;" :class="loading ? 'bg-amber-400' : 'bg-emerald-400'" />
          {{ loading ? '读取 ADS' : '离线数据就绪' }}
        </span>
        <div class="flex items-center gap-4 text-sm">
          <div class="text-center" style="padding-right: 12px; border-right: 1px solid rgba(100, 116, 139, 0.2);">
            <div class="text-slate-500" style="font-size: 10px;">样本</div>
            <div class="font-bold text-slate-200 font-mono">{{ formatInt(bundle?.overview.sampleCount || 0) }}</div>
          </div>
          <div class="text-center" style="padding-right: 12px; border-right: 1px solid rgba(100, 116, 139, 0.2);">
            <div class="text-slate-500" style="font-size: 10px;">患病率</div>
            <div class="font-bold text-slate-200 font-mono">{{ formatPercent(bundle?.overview.prevalenceRate || 0, 1) }}</div>
          </div>
          <div class="text-center">
            <div class="text-slate-500" style="font-size: 10px;">AUC</div>
            <div class="font-bold text-slate-200 font-mono">{{ (bundle?.overview.modelAuc || 0).toFixed(2) }}</div>
          </div>
        </div>
        <div class="text-right">
          <div class="font-mono text-cyan-300" style="font-size: 18px; font-weight: 600; letter-spacing: 0.5px;">{{ now.toLocaleTimeString('zh-CN', { hour12: false }) }}</div>
          <div class="text-slate-500" style="font-size: 10px;">{{ formatDateTime(now) }}</div>
        </div>
        <button
          class="px-3 py-1.5 rounded-lg bg-cyan-600/20 border border-cyan-500/30 text-cyan-300 text-xs hover:bg-cyan-600/30 transition-colors"
          @click="refresh"
        >
          ↻ 刷新
        </button>
      </div>
    </header>

    <div v-if="error" class="relative z-10 mx-6 mt-2 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
      {{ error }}
    </div>

    <!-- Dashboard Grid -->
    <main class="relative z-10 grid grid-cols-12 gap-4 p-5 h-[calc(100vh-4.5rem)]">
      <!-- Left Column -->
      <section class="col-span-3 flex flex-col gap-4 overflow-hidden">
        <div class="tech-card p-5 flex-shrink-0">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-slate-200" style="font-size: 14px; padding-bottom: 6px; border-bottom: 2px solid rgba(34, 211, 238, 0.15);">总览指标</h3>
            <div class="flex gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-cyan-400" style="animation: pulseDot 1.4s ease-in-out infinite" />
              <span class="w-1.5 h-1.5 rounded-full bg-cyan-400" style="animation: pulseDot 1.4s ease-in-out 0.2s infinite" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 mb-3">
            <StatTile label="样本总数" :value="formatCompact(bundle?.overview.sampleCount || 0)" hint="多数据集汇聚" tone="teal" />
            <StatTile label="阳性病例" :value="formatCompact(bundle?.overview.positiveCount || 0)" hint="高风险样本" tone="red" />
            <StatTile label="患病率" :value="formatPercent(bundle?.overview.prevalenceRate || 0, 1)" hint="总体基线" tone="amber" />
            <StatTile label="模型 AUC" :value="(bundle?.overview.modelAuc || 0).toFixed(2)" hint="当前最佳基线" tone="slate" />
          </div>
          <EChart :option="overviewOption" height="180px" />
        </div>

        <div class="tech-card p-5 flex-1 min-h-0 flex flex-col">
          <h3 class="font-semibold text-slate-200 mb-2" style="font-size: 14px; padding-bottom: 6px; border-bottom: 2px solid rgba(34, 211, 238, 0.15);">年龄分层</h3>
          <div class="flex-1 min-h-0">
            <EChart :option="ageOption" height="100%" />
          </div>
        </div>

        <div class="tech-card p-5 flex-1 min-h-0 flex flex-col">
          <h3 class="font-semibold text-slate-200 mb-2" style="font-size: 14px; padding-bottom: 6px; border-bottom: 2px solid rgba(34, 211, 238, 0.15);">生活方式分析</h3>
          <div class="flex-1 min-h-0">
            <EChart :option="lifestyleOption" height="100%" />
          </div>
        </div>
      </section>

      <!-- Center Column -->
      <section class="col-span-5 flex flex-col gap-4 overflow-hidden">
        <div class="tech-card p-5 flex-1 min-h-0 flex flex-col">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-slate-200" style="font-size: 14px; padding-bottom: 6px; border-bottom: 2px solid rgba(34, 211, 238, 0.15);">UCI 临床指标</h3>
            <div class="flex gap-1.5 flex-wrap">
              <button
                v-for="item in bundle?.clinical.items || []"
                :key="item.feature"
                class="rounded transition-all"
                style="padding: 3px 10px; font-size: 11px;"
                :class="selectedClinicalFeature === item.feature
                  ? 'bg-cyan-600/30 text-cyan-300 border border-cyan-500/40'
                  : 'text-slate-400 hover:text-slate-300 border border-transparent'"
                @click="selectedClinicalFeature = item.feature"
              >
                {{ item.label }}
              </button>
            </div>
          </div>
          <div class="flex-1 min-h-0">
            <EChart :option="clinicalOption" height="100%" />
          </div>
        </div>

        <div class="tech-card p-5 flex-1 min-h-0 flex flex-col">
          <h3 class="font-semibold text-slate-200 mb-2" style="font-size: 14px; padding-bottom: 6px; border-bottom: 2px solid rgba(34, 211, 238, 0.15);">模型评估</h3>
          <EChart :option="metricsOption" height="200px" />
          <div class="mt-2 space-y-1.5 overflow-y-auto flex-1 min-h-0">
            <div v-for="item in importanceBars" :key="item.label" class="flex items-center gap-2 text-xs">
              <span class="w-20 text-slate-400 truncate text-right">{{ item.label }}</span>
              <div class="flex-1 h-3 bg-slate-800/50 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="{
                    'bg-gradient-to-r from-red-500 to-red-400': item.tone === 'high',
                    'bg-gradient-to-r from-amber-500 to-amber-400': item.tone === 'medium',
                    'bg-gradient-to-r from-teal-500 to-teal-400': item.tone === 'low',
                  }"
                  :style="{ width: item.width }"
                />
              </div>
              <span class="w-10 text-slate-300 font-mono">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Right Column -->
      <section class="col-span-4 flex flex-col gap-4 overflow-hidden">
        <!-- Feature Importance -->
        <div class="tech-card p-5 flex-1 min-h-0 flex flex-col">
          <h3 class="font-semibold text-slate-200 mb-3" style="font-size: 14px; padding-bottom: 6px; border-bottom: 2px solid rgba(34, 211, 238, 0.15);">特征重要性排名</h3>
          <div class="space-y-2 overflow-y-auto flex-1 min-h-0">
            <div v-for="item in importanceBars" :key="item.label" class="flex items-center gap-2.5">
              <span class="w-24 text-slate-400 truncate text-right" style="font-size: 13px;">{{ item.label }}</span>
              <div class="flex-1 h-4 bg-slate-800/50 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="{
                    'bg-gradient-to-r from-red-500 to-red-400': item.tone === 'high',
                    'bg-gradient-to-r from-amber-500 to-amber-400': item.tone === 'medium',
                    'bg-gradient-to-r from-teal-500 to-teal-400': item.tone === 'low',
                  }"
                  :style="{ width: item.width }"
                />
              </div>
              <span class="w-12 text-slate-300 font-mono text-right" style="font-size: 13px;">{{ item.value }}</span>
            </div>
          </div>
        </div>

        <div class="tech-card p-5 flex-1 min-h-0 overflow-y-auto">
          <h3 class="font-semibold text-slate-200 mb-3" style="font-size: 14px; padding-bottom: 6px; border-bottom: 2px solid rgba(34, 211, 238, 0.15);">共病概览</h3>
          <div class="space-y-2.5">
            <div v-for="slice in bundle?.derived.comorbidity || []" :key="slice.label" class="rounded-lg bg-slate-700/30 border border-slate-700/30" style="padding: 10px 12px;">
              <div class="flex justify-between items-center">
                <span class="text-slate-300" style="font-size: 13px;">{{ slice.label }}</span>
                <span class="font-bold font-mono" style="font-size: 13px;" :class="{
                  'text-red-400': slice.tone === 'high',
                  'text-amber-400': slice.tone === 'medium',
                  'text-teal-400': slice.tone === 'low',
                }">{{ slice.value }}</span>
              </div>
              <div class="flex justify-between mt-1 text-slate-500" style="font-size: 11px;">
                <span>{{ formatInt(slice.sampleCount) }} 样本</span>
                <span>{{ formatPercent(slice.prevalenceRate, 1) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="tech-card p-5 flex-shrink-0">
          <h3 class="font-semibold text-slate-200 mb-3" style="font-size: 14px; padding-bottom: 6px; border-bottom: 2px solid rgba(34, 211, 238, 0.15);">数据集清单</h3>
          <div class="space-y-2.5">
            <div v-for="ds in bundle?.overview.datasets || []" :key="ds.name" class="rounded bg-slate-700/30 border border-slate-700/30" style="padding: 10px 12px;">
              <div class="font-medium text-slate-300" style="font-size: 13px;">{{ ds.name }}</div>
              <div class="text-slate-500 mt-1" style="font-size: 11px;">
                {{ formatInt(ds.rows) }} 行 · {{ ds.columns }} 列 · {{ ds.target }}
              </div>
              <div class="mt-1" style="font-size: 11px; color: rgba(34, 211, 238, 0.6);">{{ ds.usage }}</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
