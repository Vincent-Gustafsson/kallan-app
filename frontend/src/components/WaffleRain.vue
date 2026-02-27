<script setup lang="ts">
import { ref } from "vue";

const props = withDefaults(
  defineProps<{
    count?: number;
    zIndex?: string; // lets you layer it easily
  }>(),
  {
    count: 30,
    zIndex: "z-0",
  },
);

type WaffleStyle = Record<string, string | number>;

function makeWaffleStyle(): WaffleStyle {
  const left = Math.floor(Math.random() * 100);
  const duration = Math.random() * 7 + 5;
  const delay = Math.random() * -12;
  const size = Math.random() * 2.5 + 1.5;
  const rotationSpeed = Math.random() > 0.5 ? 1 : -1;

  return {
    left: `${left}vw`,
    animationDuration: `${duration}s`,
    animationDelay: `${delay}s`,
    fontSize: `${size}rem`,
    "--rotation-direction": rotationSpeed,
  };
}

// generate once so it doesn't reshuffle on re-render
const waffleStyles = ref<WaffleStyle[]>(
  Array.from({ length: props.count }, () => makeWaffleStyle()),
);
</script>

<template>
  <div
    aria-hidden="true"
    class="bg-base-300 fixed inset-0 pointer-events-none overflow-hidden select-none"
    :class="props.zIndex"
  >
    <div
      v-for="(style, i) in waffleStyles"
      :key="i"
      class="waffle-emoji absolute -top-20"
      :style="style"
    >
      🧇
    </div>
  </div>
</template>

<style scoped>
.waffle-emoji {
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
