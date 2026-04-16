<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const emit = defineEmits<{ 'toggle-sidebar': [] }>();
const route = useRoute();
const router = useRouter();
const showUserMenu = ref(false);

const pageTitle: Record<string, string> = {
  'analysis-age': '年龄分布分析',
  'analysis-lifestyle': '生活方式分析',
  'analysis-clinical': '临床指标分析',
  'analysis-correlation': '相关性分析',
  'analysis-compare': '综合对比分析',
  'ml-training': '模型训练管理',
  'ml-comparison': '模型性能对比',
  'ml-importance': '特征重要性',
  'ml-predict': '在线风险预测',
  'data-overview': '数据概览',
  'data-cleaning': '数据清洗记录',
  'data-warehouse': '数仓分层管理',
  'system-monitor': 'Hadoop 集群监控',
  'system-logs': '系统操作日志',
  'system-users': '用户管理',
  'personal-profile': '个人资料',
  'personal-history': '预测历史',
  'personal-reports': '分析报告',
};

const title = computed(() => pageTitle[route.name as string] || '');

const handleLogout = () => router.push('/login');
</script>

<template>
  <!-- Clean, minimal header: page title left, controls right -->
  <header class="h-[64px] flex items-center justify-between px-10 shrink-0" style="border-bottom: 1px solid #162033;">
    <!-- Left: toggle + page title -->
    <div class="flex items-center gap-4">
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-300 transition-colors"
        @click="emit('toggle-sidebar')"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5"/>
        </svg>
      </button>
      <h1 class="text-lg font-semibold text-white">{{ title }}</h1>
    </div>

    <!-- Right: minimal controls -->
    <div class="flex items-center gap-3">
      <!-- Notification -->
      <button class="relative w-9 h-9 flex items-center justify-center rounded-xl text-slate-500 hover:text-slate-300 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"/>
        </svg>
        <span class="absolute top-1 right-1 w-2 h-2 bg-cyan-400 rounded-full"></span>
      </button>

      <!-- User -->
      <div class="relative">
        <button
          class="flex items-center gap-2.5 py-1.5 px-2 rounded-xl hover:bg-white/[0.04] transition-colors"
          @click="showUserMenu = !showUserMenu"
        >
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center text-white text-xs font-bold">管</div>
          <span class="text-sm text-slate-300">管理员</span>
        </button>

        <div v-if="showUserMenu" class="absolute right-0 top-full mt-2 w-44 py-1.5 rounded-xl shadow-2xl z-50" style="background: #162033; border: 1px solid #1e2d42;">
          <button class="w-full px-4 py-2.5 text-sm text-left text-slate-300 hover:text-white hover:bg-white/[0.06] transition-colors" @click="router.push('/personal/profile'); showUserMenu = false">个人资料</button>
          <button class="w-full px-4 py-2.5 text-sm text-left text-slate-300 hover:text-white hover:bg-white/[0.06] transition-colors" @click="router.push('/personal/history'); showUserMenu = false">预测历史</button>
          <div class="mx-3 my-1" style="border-top: 1px solid #1e2d42;"></div>
          <button class="w-full px-4 py-2.5 text-sm text-left text-red-400 hover:bg-red-500/10 transition-colors" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </div>
  </header>
  <div v-if="showUserMenu" class="fixed inset-0 z-30" @click="showUserMenu = false" />
</template>
