<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  modelValue: number;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", v: number): void;
}>();

const MIN = 1;
const MAX = 10;

const canDec = computed(() => props.modelValue > MIN);
const canInc = computed(() => props.modelValue < MAX);

function dec() {
  emit("update:modelValue", Math.max(MIN, props.modelValue - 1));
}

function inc() {
  emit("update:modelValue", Math.min(MAX, props.modelValue + 1));
}
</script>

<template>
  <div class="join">
    <button class="btn btn-xl btn-secondary join-item" :disabled="!canDec" @click.prevent="dec">
      −
    </button>

    <div
      class="input input-bordered input-xl join-item flex-none w-[4ch] flex items-center justify-center text-2xl pointer-events-none select-none tabular-nums"
    >
      {{ modelValue }}
    </div>

    <button class="btn btn-xl btn-secondary join-item" :disabled="!canInc" @click.prevent="inc">
      +
    </button>
  </div>
</template>
