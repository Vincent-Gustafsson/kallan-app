<script setup lang="ts">
import { ref } from "vue";

const props = withDefaults(
  defineProps<{
    avatarUrls: string[];
    count?: number;
    zIndex?: string;
  }>(),
  {
    count: 20,
    zIndex: "z-0",
  },
);

type Drop = {
  src: string;
  style: Record<string, string | number>;
};

function makeDrop(): Drop {
  const left = Math.floor(Math.random() * 100);
  const duration = Math.random() * 7 + 5;
  const delay = Math.random() * -12;
  const size = Math.random() * 1.5 + 1.5; // 1.5–3rem
  const rotationSpeed = Math.random() > 0.5 ? 1 : -1;
  const src = props.avatarUrls[Math.floor(Math.random() * props.avatarUrls.length)] ?? "";

  return {
    src,
    style: {
      left: `${left}vw`,
      animationDuration: `${duration}s`,
      animationDelay: `${delay}s`,
      width: `${size}rem`,
      height: `${size}rem`,
      "--rotation-direction": rotationSpeed,
    },
  };
}

const drops = ref<Drop[]>(Array.from({ length: props.count }, () => makeDrop()));
</script>

<template>
  <div
    aria-hidden="true"
    class="bg-base-300 fixed inset-0 pointer-events-none overflow-hidden select-none"
    :class="props.zIndex"
  >
    <img
      v-for="(drop, i) in drops"
      :key="i"
      :src="drop.src"
      alt=""
      class="avatar-drop absolute -top-20 rounded-full object-cover opacity-60"
      :style="drop.style"
    />
  </div>
</template>

<style scoped>
.avatar-drop {
  will-change: transform;
  animation-name: fall;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

@keyframes fall {
  0% {
    transform: translateY(0) rotate(0deg);
  }
  100% {
    transform: translateY(110vh) rotate(calc(360deg * var(--rotation-direction, 1) * 2));
  }
}
</style>
