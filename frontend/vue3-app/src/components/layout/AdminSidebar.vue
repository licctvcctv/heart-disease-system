<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const props = defineProps<{ collapsed: boolean }>();
const router = useRouter();
const route = useRoute();

interface MenuItem { key: string; label: string; route?: string; }
interface MenuGroup { title: string; items: MenuItem[]; }

const menuGroups: MenuGroup[] = [
  {
    title: '数据分析',
    items: [
      { key: 'analysis-age', label: '年龄分布', route: '/analysis/age' },
      { key: 'analysis-lifestyle', label: '生活方式', route: '/analysis/lifestyle' },
      { key: 'analysis-clinical', label: '临床指标', route: '/analysis/clinical' },
      { key: 'analysis-correlation', label: '相关性', route: '/analysis/correlation' },
      { key: 'analysis-compare', label: '综合对比', route: '/analysis/compare' },
    ],
  },
  {
    title: '机器学习',
    items: [
      { key: 'ml-training', label: '模型训练', route: '/ml/training' },
      { key: 'ml-comparison', label: '性能对比', route: '/ml/comparison' },
      { key: 'ml-importance', label: '特征重要性', route: '/ml/importance' },
      { key: 'ml-predict', label: '风险预测', route: '/ml/predict' },
    ],
  },
  {
    title: '数据治理',
    items: [
      { key: 'data-overview', label: '数据概览', route: '/data/overview' },
      { key: 'data-cleaning', label: '清洗记录', route: '/data/cleaning' },
      { key: 'data-warehouse', label: '数仓分层', route: '/data/warehouse' },
    ],
  },
  {
    title: '系统',
    items: [
      { key: 'system-monitor', label: '集群监控', route: '/system/monitor' },
      { key: 'system-logs', label: '操作日志', route: '/system/logs' },
      { key: 'system-users', label: '用户管理', route: '/system/users' },
    ],
  },
  {
    title: '个人',
    items: [
      { key: 'personal-profile', label: '个人资料', route: '/personal/profile' },
      { key: 'personal-history', label: '预测历史', route: '/personal/history' },
      { key: 'personal-reports', label: '分析报告', route: '/personal/reports' },
    ],
  },
];

const findGroupForRoute = (name: string) => {
  for (const g of menuGroups) {
    if (g.items.some(i => i.key === name)) return g.title;
  }
  return menuGroups[0].title;
};

const activeGroup = ref(findGroupForRoute(route.name as string));

watch(() => route.name, (name) => {
  activeGroup.value = findGroupForRoute(name as string);
});

const isActive = (key: string) => route.name === key;

const handleClick = (item: MenuItem) => {
  if (item.route) router.push(item.route);
};

const openBigScreen = () => {
  window.open(router.resolve({ name: 'bigscreen' }).href, '_blank');
};
</script>

<template>
  <aside
    v-if="!collapsed"
    class="w-[260px] h-screen flex flex-col shrink-0"
    style="background: #0a1628; border-right: 1px solid #162033;"
  >
    <!-- Brand -->
    <div class="px-6 pt-6 pb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white font-black text-base shadow-lg shadow-cyan-900/30">
          HD
        </div>
        <div>
          <div class="text-[15px] font-semibold text-white">心脏病分析</div>
          <div class="text-[11px] text-slate-500">数据分析与预测平台</div>
        </div>
      </div>
      <!-- Big screen entry -->
      <button
        class="mt-4 w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium text-cyan-300 transition-colors"
        style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.15);"
        @click="openBigScreen"
      >
        可视化大屏
        <span class="text-[10px] opacity-60">↗</span>
      </button>
    </div>

    <!-- Nav groups -->
    <nav class="flex-1 overflow-y-auto px-3 pb-4">
      <div v-for="group in menuGroups" :key="group.title" class="mb-1">
        <!-- Group header: clickable, toggles which group is open -->
        <button
          class="w-full flex items-center justify-between px-3 py-3 rounded-lg text-[13px] font-semibold transition-colors"
          :class="activeGroup === group.title ? 'text-slate-200' : 'text-slate-500 hover:text-slate-300'"
          @click="activeGroup = activeGroup === group.title ? '' : group.title"
        >
          {{ group.title }}
          <svg
            class="w-3.5 h-3.5 transition-transform duration-200"
            :class="activeGroup === group.title ? 'rotate-180' : ''"
            fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
          ><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        </button>

        <!-- Items: only visible for active group -->
        <div v-if="activeGroup === group.title" class="pb-2">
          <button
            v-for="item in group.items"
            :key="item.key"
            class="w-full text-left px-4 py-3 rounded-xl mb-0.5 text-[14px] transition-all duration-150"
            :class="isActive(item.key)
              ? 'text-white font-medium'
              : 'text-slate-400 hover:text-slate-200'"
            :style="isActive(item.key) ? 'background: rgba(6, 182, 212, 0.1); box-shadow: inset 3px 0 0 #22d3ee;' : ''"
            @click="handleClick(item)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </nav>

    <!-- Footer -->
    <div class="px-6 py-4 text-[11px] text-slate-700" style="border-top: 1px solid #162033;">
      Hive · Django · Vue3 · ECharts
    </div>
  </aside>

  <!-- Collapsed: thin icon strip -->
  <aside
    v-else
    class="w-[60px] h-screen flex flex-col items-center shrink-0 py-4 gap-2"
    style="background: #0a1628; border-right: 1px solid #162033;"
  >
    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white font-black text-xs mb-4">
      HD
    </div>
    <button
      v-for="group in menuGroups"
      :key="group.title"
      class="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-semibold transition-all"
      :class="activeGroup === group.title ? 'text-cyan-400' : 'text-slate-600 hover:text-slate-400'"
      :style="activeGroup === group.title ? 'background: rgba(6, 182, 212, 0.1);' : ''"
      :title="group.title"
      @click="activeGroup = group.title; handleClick(group.items[0])"
    >
      {{ group.title.charAt(0) }}
    </button>
  </aside>
</template>
