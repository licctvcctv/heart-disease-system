<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import ParticleBackground from '@/components/ParticleBackground.vue';

const router = useRouter();
const message = useMessage();
const loading = ref(false);
const activeTab = ref('login');

const loginForm = ref({ username: '', password: '' });
const registerForm = ref({ username: '', password: '', confirmPassword: '', phone: '' });

onMounted(() => {
  document.body.classList.add('dark-body');
});

onBeforeUnmount(() => {
  document.body.classList.remove('dark-body');
});

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    message.warning('请填写用户名和密码');
    return;
  }
  loading.value = true;
  await new Promise(r => setTimeout(r, 800));
  loading.value = false;
  message.success('登录成功');
  router.push('/');
};

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    message.warning('请填写完整信息');
    return;
  }
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    message.error('两次密码输入不一致');
    return;
  }
  loading.value = true;
  await new Promise(r => setTimeout(r, 800));
  loading.value = false;
  message.success('注册成功，请登录');
  activeTab.value = 'login';
};
</script>

<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
    <ParticleBackground />
    <div class="grid-overlay" />

    <div style="position: relative; z-index: 10; width: 100%; max-width: 420px; padding: 0 16px;">
      <!-- Brand -->
      <div style="text-align: center; margin-bottom: 32px;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 16px; background: linear-gradient(135deg, #06b6d4, #2563eb); margin-bottom: 16px; box-shadow: 0 8px 24px rgba(6, 182, 212, 0.2);">
          <span style="font-size: 24px; font-weight: 900; color: white;">HD</span>
        </div>
        <h1 style="color: white; font-size: 22px; font-weight: 700; margin-bottom: 4px;">心脏病健康数据分析系统</h1>
        <p style="color: #64748b; font-size: 14px;">基于 Hive 数仓 · 机器学习智能预测</p>
      </div>

      <!-- Form Card -->
      <n-card style="background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(24px); border: 1px solid rgba(51, 65, 85, 0.5); border-radius: 16px;">
        <n-tabs v-model:value="activeTab" type="segment" animated>
          <n-tab-pane name="login" tab="登录">
            <n-form @submit.prevent="handleLogin" style="margin-top: 8px;">
              <n-form-item label="用户名">
                <n-input
                  v-model:value="loginForm.username"
                  placeholder="请输入用户名"
                />
              </n-form-item>
              <n-form-item label="密码">
                <n-input
                  v-model:value="loginForm.password"
                  type="password"
                  show-password-on="click"
                  placeholder="请输入密码"
                />
              </n-form-item>
              <n-button
                type="primary"
                block
                strong
                :loading="loading"
                @click="handleLogin"
                style="margin-top: 8px;"
              >
                {{ loading ? '登录中...' : '登 录' }}
              </n-button>
            </n-form>
          </n-tab-pane>

          <n-tab-pane name="register" tab="注册">
            <n-form @submit.prevent="handleRegister" style="margin-top: 8px;">
              <n-form-item label="用户名">
                <n-input
                  v-model:value="registerForm.username"
                  placeholder="请输入用户名"
                />
              </n-form-item>
              <n-form-item label="手机号">
                <n-input
                  v-model:value="registerForm.phone"
                  placeholder="请输入手机号"
                />
              </n-form-item>
              <n-form-item label="密码">
                <n-input
                  v-model:value="registerForm.password"
                  type="password"
                  show-password-on="click"
                  placeholder="请输入密码"
                />
              </n-form-item>
              <n-form-item label="确认密码">
                <n-input
                  v-model:value="registerForm.confirmPassword"
                  type="password"
                  show-password-on="click"
                  placeholder="请再次输入密码"
                />
              </n-form-item>
              <n-button
                type="primary"
                block
                strong
                :loading="loading"
                @click="handleRegister"
                style="margin-top: 8px;"
              >
                {{ loading ? '注册中...' : '注 册' }}
              </n-button>
            </n-form>
          </n-tab-pane>
        </n-tabs>

        <!-- Footer -->
        <div style="margin-top: 24px; text-align: center; font-size: 12px; color: #64748b;">
          Hadoop · Hive · Django · Vue3 · ECharts · CatBoost
        </div>
      </n-card>
    </div>
  </div>
</template>
