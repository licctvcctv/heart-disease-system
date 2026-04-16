<script setup lang="ts">
defineProps<{
  label: string;
  value: string;
  hint?: string;
  tone?: 'teal' | 'red' | 'amber' | 'slate';
}>();

const borderColor: Record<string, string> = {
  teal: 'border-l-teal-400',
  red: 'border-l-red-400',
  amber: 'border-l-amber-400',
  slate: 'border-l-slate-400',
};

const valueColor: Record<string, string> = {
  teal: 'text-teal-300',
  red: 'text-red-300',
  amber: 'text-amber-300',
  slate: 'text-slate-300',
};
</script>

<template>
  <div
    class="rounded-lg bg-slate-800/40 border border-slate-700/30 border-l-2 px-3 py-2"
    :class="borderColor[tone || 'slate']"
  >
    <div class="text-[10px] text-slate-500 leading-tight">{{ label }}</div>
    <div class="text-lg font-bold font-mono leading-tight mt-0.5" :class="valueColor[tone || 'slate']">{{ value }}</div>
    <div v-if="hint" class="text-[9px] text-slate-600 mt-0.5">{{ hint }}</div>
  </div>
</template>
