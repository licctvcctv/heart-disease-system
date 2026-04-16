<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
}>();
</script>

<template>
  <section class="panel-card">
    <header class="panel-card__header">
      <div class="panel-card__title-wrap">
        <h2 class="panel-card__title">{{ title }}</h2>
        <p v-if="subtitle" class="panel-card__subtitle">{{ subtitle }}</p>
      </div>
      <div class="panel-card__signals" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <slot name="actions" />
    </header>
    <div class="panel-card__body">
      <slot />
    </div>
  </section>
</template>
