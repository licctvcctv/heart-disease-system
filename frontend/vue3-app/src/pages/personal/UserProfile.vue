<script setup lang="ts">
import { ref, inject, onMounted } from 'vue';
import { NCard, NSpace, NAvatar, NForm, NFormItem, NInput, NButton, NGrid, NGridItem } from 'naive-ui';

const message = inject<any>('message');

const PROFILE_KEY = 'user_profile';

const profile = ref({
  username: '',
  nickname: '',
  phone: '',
  email: '',
  role: '',
  regDate: '',
  bio: '',
});

const passwords = ref({ old: '', new1: '', new2: '' });

const loadProfile = () => {
  const username = localStorage.getItem('username') || '';
  const saved = localStorage.getItem(PROFILE_KEY);
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      profile.value = { ...profile.value, ...parsed };
    } catch {
      // ignore
    }
  }
  if (username) {
    profile.value.username = username;
    if (!profile.value.nickname) {
      profile.value.nickname = username;
    }
  }
  if (!profile.value.role) {
    profile.value.role = username === 'admin' ? '管理员' : '普通用户';
  }
  if (!profile.value.regDate) {
    profile.value.regDate = new Date().toLocaleDateString('zh-CN');
  }
};

onMounted(() => {
  loadProfile();
});

const saveProfile = () => {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile.value));
  if (profile.value.username) {
    localStorage.setItem('username', profile.value.username);
  }
  message?.success('个人资料保存成功');
};

const changePassword = () => {
  if (!passwords.value.old || !passwords.value.new1) {
    message?.warning('请填写完整密码信息');
    return;
  }
  if (passwords.value.new1 !== passwords.value.new2) {
    message?.error('两次密码不一致');
    return;
  }
  message?.success('密码修改成功');
  passwords.value = { old: '', new1: '', new2: '' };
};
</script>

<template>
  <n-space vertical :size="24" style="max-width: 720px; margin: 0 auto;">
    <!-- Avatar & Basic Info -->
    <n-card title="个人资料">
      <template #header-extra>
        <span style="font-size: 13px; color: #94a3b8;">管理您的账户信息和安全设置</span>
      </template>

      <n-space align="center" :size="24" style="margin-bottom: 24px;">
        <n-avatar
          :size="80"
          round
          :style="{ backgroundColor: '#06b6d4', fontSize: '28px', fontWeight: 'bold' }"
        >
          {{ profile.nickname ? profile.nickname.charAt(0) : '?' }}
        </n-avatar>
        <n-space vertical :size="4">
          <span style="font-size: 18px; font-weight: 700;">{{ profile.nickname || '未设置' }}</span>
          <span style="font-size: 13px; color: #94a3b8;">{{ profile.role || '未分配角色' }}</span>
          <span v-if="profile.regDate" style="font-size: 12px; color: #64748b;">注册于 {{ profile.regDate }}</span>
        </n-space>
      </n-space>

      <n-form label-placement="top" label-width="auto">
        <n-grid :cols="2" :x-gap="16" :y-gap="4">
          <n-grid-item>
            <n-form-item label="用户名">
              <n-input v-model:value="profile.username" placeholder="未设置" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="昵称">
              <n-input v-model:value="profile.nickname" placeholder="请输入昵称" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="手机号">
              <n-input v-model:value="profile.phone" placeholder="请输入手机号" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="邮箱">
              <n-input v-model:value="profile.email" placeholder="请输入邮箱" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="2">
            <n-form-item label="个人简介">
              <n-input v-model:value="profile.bio" type="textarea" :rows="2" placeholder="请输入个人简介" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>

      <n-space justify="end" style="margin-top: 8px;">
        <n-button type="primary" @click="saveProfile">保存修改</n-button>
      </n-space>
    </n-card>

    <!-- Change Password -->
    <n-card title="修改密码">
      <n-form label-placement="top" label-width="auto" style="max-width: 400px;">
        <n-form-item label="当前密码">
          <n-input v-model:value="passwords.old" type="password" show-password-on="click" placeholder="请输入当前密码" />
        </n-form-item>
        <n-form-item label="新密码">
          <n-input v-model:value="passwords.new1" type="password" show-password-on="click" placeholder="请输入新密码" />
        </n-form-item>
        <n-form-item label="确认新密码">
          <n-input v-model:value="passwords.new2" type="password" show-password-on="click" placeholder="请再次输入新密码" />
        </n-form-item>
        <n-form-item>
          <n-button @click="changePassword">更新密码</n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </n-space>
</template>
