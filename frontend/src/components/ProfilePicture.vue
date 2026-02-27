<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    avatarUrl: string;
    sizeClass?: string;
    ringColorClass?: string;
  }>(),
  {
    sizeClass: "size-30",
    ringColorClass: "ring-primary",
  },
);
</script>

<template>
  <div class="avatar">
    <div
      :class="[
        'ring-offset-base-100 rounded-full ring-2 ring-offset-2 overflow-hidden',
        props.sizeClass,
        props.ringColorClass,
      ]"
    >
      <img :src="props.avatarUrl" alt="Avatar" loading="lazy" />
    </div>
  </div>
</template>
