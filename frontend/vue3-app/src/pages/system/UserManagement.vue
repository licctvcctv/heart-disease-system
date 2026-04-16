<script setup lang="ts">
import { ref, h, onMounted, inject } from 'vue';
import { NCard, NSpace, NDataTable, NTag, NButton, NModal, NForm, NFormItem, NInput, NSelect } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';

const message = inject<any>('message');

const USERS_KEY = 'system_users';

interface UserRecord {
  id: number;
  username: string;
  role: string;
  status: string;
}

const defaultUsers: UserRecord[] = [
  { id: 1, username: 'admin', role: '管理员', status: '启用' },
  { id: 2, username: 'user1', role: '普通用户', status: '启用' },
];

const users = ref<UserRecord[]>([]);
const showModal = ref(false);
const newUser = ref({ username: '', role: '普通用户' });

const roleOptions = [
  { label: '管理员', value: '管理员' },
  { label: '普通用户', value: '普通用户' },
];

const loadUsers = () => {
  const saved = localStorage.getItem(USERS_KEY);
  if (saved) {
    try {
      users.value = JSON.parse(saved);
    } catch {
      users.value = [...defaultUsers];
    }
  } else {
    users.value = [...defaultUsers];
  }
};

const saveUsers = () => {
  localStorage.setItem(USERS_KEY, JSON.stringify(users.value));
};

const toggleStatus = (row: UserRecord) => {
  row.status = row.status === '启用' ? '禁用' : '启用';
  saveUsers();
  message?.success(`用户 ${row.username} 已${row.status}`);
};

const deleteUser = (row: UserRecord) => {
  if (row.username === 'admin') {
    message?.warning('不能删除管理员账户');
    return;
  }
  users.value = users.value.filter((u) => u.id !== row.id);
  saveUsers();
  message?.success(`用户 ${row.username} 已删除`);
};

const addUser = () => {
  if (!newUser.value.username.trim()) {
    message?.warning('请输入用户名');
    return;
  }
  if (users.value.some((u) => u.username === newUser.value.username.trim())) {
    message?.error('用户名已存在');
    return;
  }
  const maxId = users.value.reduce((max, u) => Math.max(max, u.id), 0);
  users.value.push({
    id: maxId + 1,
    username: newUser.value.username.trim(),
    role: newUser.value.role,
    status: '启用',
  });
  saveUsers();
  showModal.value = false;
  newUser.value = { username: '', role: '普通用户' };
  message?.success('用户添加成功');
};

const columns: DataTableColumns<UserRecord> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '用户名', key: 'username', width: 160 },
  {
    title: '角色',
    key: 'role',
    width: 120,
    render(row) {
      return h(NTag, { type: row.role === '管理员' ? 'warning' : 'info', size: 'small', bordered: false }, () => row.role);
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      return h(NTag, { type: row.status === '启用' ? 'success' : 'error', size: 'small', bordered: false }, () => row.status);
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render(row) {
      return h(NSpace, { size: 8 }, () => [
        h(
          NButton,
          { size: 'small', onClick: () => toggleStatus(row) },
          () => (row.status === '启用' ? '禁用' : '启用'),
        ),
        h(
          NButton,
          { size: 'small', type: 'error', onClick: () => deleteUser(row), disabled: row.username === 'admin' },
          () => '删除',
        ),
      ]);
    },
  },
];

onMounted(() => {
  loadUsers();
});
</script>

<template>
  <n-space vertical :size="24">
    <n-card title="用户管理">
      <template #header-extra>
        <n-button type="primary" size="small" @click="showModal = true">添加用户</n-button>
      </template>

      <n-data-table :columns="columns" :data="users" :bordered="false" size="small" />
    </n-card>

    <n-modal v-model:show="showModal" preset="card" title="添加用户" style="max-width: 420px;">
      <n-form label-placement="top" label-width="auto">
        <n-form-item label="用户名">
          <n-input v-model:value="newUser.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="角色">
          <n-select v-model:value="newUser.role" :options="roleOptions" />
        </n-form-item>
      </n-form>
      <n-space justify="end" style="margin-top: 16px;">
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" @click="addUser">确认添加</n-button>
      </n-space>
    </n-modal>
  </n-space>
</template>
