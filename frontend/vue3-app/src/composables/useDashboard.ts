import { onBeforeUnmount, onMounted, ref } from 'vue';
import { loadDashboardBundle } from '@/services/dashboardService';
import type { DashboardBundle } from '@/types/dashboard';

export function useDashboard() {
  const bundle = ref<DashboardBundle | null>(null);
  const loading = ref(true);
  const error = ref<string | null>(null);
  const now = ref(new Date());

  let timer: number | undefined;

  const refresh = async () => {
    loading.value = true;
    error.value = null;
    try {
      bundle.value = await loadDashboardBundle();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载失败';
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    void refresh();
    timer = window.setInterval(() => {
      now.value = new Date();
    }, 1000);
  });

  onBeforeUnmount(() => {
    if (timer) {
      window.clearInterval(timer);
    }
  });

  return {
    bundle,
    loading,
    error,
    now,
    refresh,
  };
}
