import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/AuthPage.vue'),
    },
    {
      path: '/bigscreen',
      name: 'bigscreen',
      component: () => import('@/pages/BigScreen.vue'),
    },
    {
      path: '/',
      component: () => import('@/components/layout/AdminLayout.vue'),
      redirect: '/analysis/age',
      children: [
        // 数据分析中心
        { path: 'analysis/age', name: 'analysis-age', component: () => import('@/pages/analysis/AnalysisAge.vue') },
        { path: 'analysis/lifestyle', name: 'analysis-lifestyle', component: () => import('@/pages/analysis/AnalysisLifestyle.vue') },
        { path: 'analysis/clinical', name: 'analysis-clinical', component: () => import('@/pages/analysis/AnalysisClinical.vue') },
        { path: 'analysis/correlation', name: 'analysis-correlation', component: () => import('@/pages/analysis/AnalysisCorrelation.vue') },
        { path: 'analysis/compare', name: 'analysis-compare', component: () => import('@/pages/analysis/AnalysisCompare.vue') },
        // 机器学习引擎
        { path: 'ml/training', name: 'ml-training', component: () => import('@/pages/ml/ModelTraining.vue') },
        { path: 'ml/comparison', name: 'ml-comparison', component: () => import('@/pages/ml/ModelComparison.vue') },
        { path: 'ml/importance', name: 'ml-importance', component: () => import('@/pages/ml/FeatureImportance.vue') },
        { path: 'ml/predict', name: 'ml-predict', component: () => import('@/pages/ml/RiskPrediction.vue') },
        // 数据治理中心
        { path: 'data/overview', name: 'data-overview', component: () => import('@/pages/data/DataOverview.vue') },
        { path: 'data/cleaning', name: 'data-cleaning', component: () => import('@/pages/data/DataCleaning.vue') },
        { path: 'data/warehouse', name: 'data-warehouse', component: () => import('@/pages/data/WarehouseLayers.vue') },
        // 系统运维
        { path: 'system/monitor', name: 'system-monitor', component: () => import('@/pages/system/SystemMonitor.vue') },
        { path: 'system/logs', name: 'system-logs', component: () => import('@/pages/system/SystemLogs.vue') },
        { path: 'system/users', name: 'system-users', component: () => import('@/pages/system/UserManagement.vue') },
        // 个人中心
        { path: 'personal/profile', name: 'personal-profile', component: () => import('@/pages/personal/UserProfile.vue') },
        { path: 'personal/history', name: 'personal-history', component: () => import('@/pages/personal/PredictionHistory.vue') },
        { path: 'personal/reports', name: 'personal-reports', component: () => import('@/pages/personal/AnalysisReports.vue') },
      ],
    },
  ],
});

export default router;
