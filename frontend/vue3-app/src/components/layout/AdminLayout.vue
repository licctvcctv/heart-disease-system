<script setup lang="ts">
import { ref, computed, h } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { NLayout, NLayoutSider, NLayoutHeader, NMenu, NIcon, NAvatar, NDropdown, NButton, NSpace } from 'naive-ui';
import type { MenuOption } from 'naive-ui';
import {
  BarChartOutline,
  PulseOutline,
  ServerOutline,
  SettingsOutline,
  PersonOutline,
  DesktopOutline,
  AnalyticsOutline,
  GitBranchOutline,
  FitnessOutline,
  FlaskOutline,
  LayersOutline,
  CloudOutline,
  DocumentTextOutline,
  PeopleOutline,
  TimeOutline,
  ReaderOutline,
} from '@vicons/ionicons5';

const router = useRouter();
const route = useRoute();
const collapsed = ref(false);

const renderIcon = (icon: any) => () => h(NIcon, null, { default: () => h(icon) });

const menuOptions = computed<MenuOption[]>(() => [
  {
    label: '可视化大屏',
    key: 'bigscreen',
    icon: renderIcon(DesktopOutline),
  },
  {
    type: 'divider',
    key: 'd1',
  },
  {
    label: '数据分析',
    key: 'analysis',
    icon: renderIcon(BarChartOutline),
    children: [
      { label: '年龄分布', key: 'analysis-age', icon: renderIcon(PeopleOutline) },
      { label: '生活方式', key: 'analysis-lifestyle', icon: renderIcon(PulseOutline) },
      { label: '临床指标', key: 'analysis-clinical', icon: renderIcon(FitnessOutline) },
      { label: '相关性', key: 'analysis-correlation', icon: renderIcon(GitBranchOutline) },
      { label: '综合对比', key: 'analysis-compare', icon: renderIcon(AnalyticsOutline) },
    ],
  },
  {
    label: '机器学习',
    key: 'ml',
    icon: renderIcon(FlaskOutline),
    children: [
      { label: '模型训练', key: 'ml-training', icon: renderIcon(SettingsOutline) },
      { label: '性能对比', key: 'ml-comparison', icon: renderIcon(BarChartOutline) },
      { label: '特征重要性', key: 'ml-importance', icon: renderIcon(AnalyticsOutline) },
      { label: '风险预测', key: 'ml-predict', icon: renderIcon(PulseOutline) },
    ],
  },
  {
    label: '数据治理',
    key: 'data',
    icon: renderIcon(LayersOutline),
    children: [
      { label: '数据概览', key: 'data-overview', icon: renderIcon(ReaderOutline) },
      { label: '清洗记录', key: 'data-cleaning', icon: renderIcon(DocumentTextOutline) },
      { label: '数仓分层', key: 'data-warehouse', icon: renderIcon(ServerOutline) },
    ],
  },
  {
    label: '系统运维',
    key: 'system',
    icon: renderIcon(CloudOutline),
    children: [
      { label: '集群监控', key: 'system-monitor', icon: renderIcon(ServerOutline) },
      { label: '操作日志', key: 'system-logs', icon: renderIcon(TimeOutline) },
      { label: '用户管理', key: 'system-users', icon: renderIcon(PeopleOutline) },
    ],
  },
  {
    label: '个人中心',
    key: 'personal',
    icon: renderIcon(PersonOutline),
    children: [
      { label: '个人资料', key: 'personal-profile', icon: renderIcon(PersonOutline) },
      { label: '预测历史', key: 'personal-history', icon: renderIcon(TimeOutline) },
      { label: '分析报告', key: 'personal-reports', icon: renderIcon(ReaderOutline) },
    ],
  },
]);

const routeMap: Record<string, string> = {
  'analysis-age': '/analysis/age',
  'analysis-lifestyle': '/analysis/lifestyle',
  'analysis-clinical': '/analysis/clinical',
  'analysis-correlation': '/analysis/correlation',
  'analysis-compare': '/analysis/compare',
  'ml-training': '/ml/training',
  'ml-comparison': '/ml/comparison',
  'ml-importance': '/ml/importance',
  'ml-predict': '/ml/predict',
  'data-overview': '/data/overview',
  'data-cleaning': '/data/cleaning',
  'data-warehouse': '/data/warehouse',
  'system-monitor': '/system/monitor',
  'system-logs': '/system/logs',
  'system-users': '/system/users',
  'personal-profile': '/personal/profile',
  'personal-history': '/personal/history',
  'personal-reports': '/personal/reports',
};

const titleMap: Record<string, string> = {
  'analysis-age': '年龄分布分析',
  'analysis-lifestyle': '生活方式分析',
  'analysis-clinical': '临床指标分析',
  'analysis-correlation': '相关性分析',
  'analysis-compare': '综合对比分析',
  'ml-training': '模型训练管理',
  'ml-comparison': '模型性能对比',
  'ml-importance': '特征重要性分析',
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

const activeKey = computed(() => route.name as string);
const pageTitle = computed(() => titleMap[activeKey.value] || '');

const handleMenuUpdate = (key: string) => {
  if (key === 'bigscreen') {
    window.open(router.resolve({ name: 'bigscreen' }).href, '_blank');
    return;
  }
  const path = routeMap[key];
  if (path) router.push(path);
};

const userOptions = [
  { label: '个人资料', key: 'profile' },
  { label: '预测历史', key: 'history' },
  { type: 'divider', key: 'd' },
  { label: '退出登录', key: 'logout' },
];

const handleUserSelect = (key: string) => {
  if (key === 'logout') router.push('/login');
  else if (key === 'profile') router.push('/personal/profile');
  else if (key === 'history') router.push('/personal/history');
};

const defaultExpanded = computed(() => {
  const name = route.name as string;
  for (const group of menuOptions.value) {
    if (group.children?.some((c: any) => c.key === name)) {
      return [group.key as string];
    }
  }
  return ['analysis'];
});
</script>

<template>
  <n-layout has-sider style="height: 100vh;">
    <!-- Sidebar -->
    <n-layout-sider
      bordered
      :collapsed="collapsed"
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      :native-scrollbar="false"
    >
      <!-- Logo -->
      <div style="padding: 20px 20px 12px; display: flex; align-items: center; gap: 12px;">
        <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #06b6d4, #3b82f6); display: flex; align-items: center; justify-content: center; color: white; font-weight: 900; font-size: 14px; flex-shrink: 0;">
          HD
        </div>
        <div v-if="!collapsed" style="overflow: hidden;">
          <div style="font-size: 15px; font-weight: 600; white-space: nowrap;">心脏病分析</div>
          <div style="font-size: 11px; opacity: 0.4; white-space: nowrap;">数据分析与预测平台</div>
        </div>
      </div>

      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="20"
        :options="menuOptions"
        :value="activeKey"
        :default-expanded-keys="defaultExpanded"
        @update:value="handleMenuUpdate"
      />
    </n-layout-sider>

    <!-- Main -->
    <n-layout>
      <!-- Header -->
      <n-layout-header bordered style="height: 60px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 18px; font-weight: 600;">{{ pageTitle }}</span>
        <n-space align="center" :size="12">
          <n-dropdown :options="userOptions" @select="handleUserSelect">
            <n-button quaternary circle>
              <n-avatar :size="32" style="background: linear-gradient(135deg, #06b6d4, #3b82f6); cursor: pointer;">
                <span style="font-size: 13px; font-weight: 700;">管</span>
              </n-avatar>
            </n-button>
          </n-dropdown>
        </n-space>
      </n-layout-header>

      <!-- Content -->
      <n-layout-content content-style="padding: 24px;" :native-scrollbar="false">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>
