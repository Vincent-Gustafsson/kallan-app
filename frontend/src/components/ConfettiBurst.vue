<script setup lang="ts">
import { ref, onBeforeUnmount } from "vue";

const props = withDefaults(
  defineProps<{
    count?: number;
    zIndex?: string;
    durationMs?: number;
    gravity?: number; // px/s^2
    drag?: number; // 0..1 (closer to 1 = more drag)
    spread?: number; // radians, 2π = full circle
    power?: number; // base initial speed (px/s)
  }>(),
  {
    count: 160,
    zIndex: "z-50",
    durationMs: 1400,
    gravity: 1400,
    drag: 0.08,
    spread: Math.PI * 2,
    power: 900,
  },
);

type Particle = {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  rot: number;
  vr: number; // deg/s
  w: number;
  h: number;
  color: string;
  opacity: number;
};

const COLORS = [
  "#EF4444",
  "#F97316",
  "#F59E0B",
  "#EAB308",
  "#22C55E",
  "#06B6D4",
  "#3B82F6",
  "#8B5CF6",
  "#EC4899",
  "#FFFFFF",
];

function rand(min: number, max: number) {
  return Math.random() * (max - min) + min;
}
function pick<T>(arr: T[]) {
  return arr[Math.floor(Math.random() * arr.length)];
}

const particles = ref<Particle[]>([]);
const isPlaying = ref(false);

let raf = 0;
let lastT = 0;
let endAt = 0;
let nextId = 1;

function stop() {
  isPlaying.value = false;
  particles.value = [];
  if (raf) cancelAnimationFrame(raf);
  raf = 0;
}

onBeforeUnmount(stop);

function spawn(x: number, y: number) {
  const now = performance.now();
  endAt = now + props.durationMs;
  lastT = now;

  // If already playing, just append a new burst on top:
  isPlaying.value = true;

  const burst: Particle[] = [];
  for (let i = 0; i < props.count; i++) {
    const angle = rand(-props.spread / 2, props.spread / 2) + -Math.PI / 2; // bias upward
    const speed = props.power * rand(0.55, 1.15);

    // small variety in sizes; rectangles look confetti-like
    const w = rand(6, 12);
    const h = w * rand(0.35, 0.75);

    burst.push({
      id: nextId++,
      x,
      y,
      vx: Math.cos(angle) * speed * rand(0.75, 1.15),
      vy: Math.sin(angle) * speed * rand(0.75, 1.15),
      rot: rand(0, 360),
      vr: rand(-720, 720),
      w,
      h,
      color: pick(COLORS),
      opacity: rand(0.85, 1),
    });
  }

  particles.value = particles.value.concat(burst);

  if (!raf) raf = requestAnimationFrame(tick);
}

function tick(t: number) {
  const dt = Math.min(0.033, (t - lastT) / 1000); // seconds, clamp
  lastT = t;

  const g = props.gravity;
  const drag = props.drag;

  // Fade out near the end
  const remaining = Math.max(0, endAt - t);
  const fade = Math.min(1, remaining / 350); // last 350ms fades

  const next = particles.value
    .map((p) => {
      // physics
      const vx = p.vx * (1 - drag * dt);
      const vy = p.vy * (1 - drag * dt) + g * dt;

      const x = p.x + vx * dt;
      const y = p.y + vy * dt;

      const rot = p.rot + p.vr * dt;

      // keep particles until time ends; also drop those way offscreen for perf
      return {
        ...p,
        x,
        y,
        vx,
        vy,
        rot,
        opacity: p.opacity * fade,
      };
    })
    .filter((p) => p.y < window.innerHeight + 200 && p.opacity > 0.03);

  particles.value = next;

  const timeUp = t >= endAt;
  if (timeUp || next.length === 0) {
    // clean up entirely
    raf = 0;
    stop();
    return;
  }

  raf = requestAnimationFrame(tick);
}

/**
 * Public API:
 * - playFromElement(el): bursts from the element center (your button)
 * - playFromPoint(x, y): bursts from screen coords
 */
function playFromElement(el: HTMLElement) {
  const r = el.getBoundingClientRect();
  spawn(r.left + r.width / 2, r.top + r.height / 2);
}

function playFromPoint(x: number, y: number) {
  spawn(x, y);
}

defineExpose({ playFromElement, playFromPoint, stop });
</script>

<template>
  <div
    v-if="isPlaying"
    aria-hidden="true"
    class="fixed inset-0 pointer-events-none overflow-hidden select-none"
    :class="props.zIndex"
  >
    <div
      v-for="p in particles"
      :key="p.id"
      class="confetti"
      :style="{
        transform: `translate3d(${p.x}px, ${p.y}px, 0) rotate(${p.rot}deg)`,
        width: `${p.w}px`,
        height: `${p.h}px`,
        backgroundColor: p.color,
        opacity: p.opacity,
      }"
    />
  </div>
</template>

<style scoped>
.confetti {
  position: absolute;
  left: 0;
  top: 0;
  border-radius: 2px;
  will-change: transform;
}
</style>
