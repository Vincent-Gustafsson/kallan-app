<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from "vue";
import { usePunishmentsStore } from "@/stores/punishments";
import PendingPunishmentCard from "@/components/PendingPunishmentCard.vue";
import ConfettiBurst from "@/components/ConfettiBurst.vue";

const punishStore = usePunishmentsStore();

const scroller = ref<HTMLElement | null>(null);
const activeIndex = ref(0);

const items = computed(() => punishStore.pending ?? []);
const showDots = computed(() => items.value.length > 1);

const burst = ref<InstanceType<typeof ConfettiBurst> | null>(null);
function playConfettiAt(x: number, y: number) {
  burst.value?.playFromPoint(x, y);
}

function scrollToIndex(i: number) {
  const el = scroller.value;
  if (!el) return;
  const child = el.querySelector<HTMLElement>(`[data-card-index="${i}"]`);
  child?.scrollIntoView({ behavior: "smooth", inline: "start", block: "nearest" });
}

function updateActiveFromScroll() {
  const el = scroller.value;
  if (!el) return;

  const cards = Array.from(el.querySelectorAll<HTMLElement>("[data-card-index]"));
  if (cards.length === 0) return;

  const scrollerRect = el.getBoundingClientRect();
  const scrollerCenter = scrollerRect.left + scrollerRect.width / 2;

  let best = 0;
  let bestDist = Number.POSITIVE_INFINITY;

  for (let i = 0; i < cards.length; i++) {
    const r = cards[i].getBoundingClientRect();
    const cardCenter = r.left + r.width / 2;
    const dist = Math.abs(cardCenter - scrollerCenter);

    if (dist < bestDist) {
      bestDist = dist;
      best = i;
    }
  }

  activeIndex.value = best;
}

let raf = 0;
let settleTimer: number | null = null;

function onScroll() {
  cancelAnimationFrame(raf);
  raf = requestAnimationFrame(updateActiveFromScroll);

  if (settleTimer) window.clearTimeout(settleTimer);
  settleTimer = window.setTimeout(updateActiveFromScroll, 120);
}

function onScrollEndLike() {
  updateActiveFromScroll();
}

watch(items, async (newItems) => {
  if (activeIndex.value > newItems.length - 1) {
    activeIndex.value = Math.max(0, newItems.length - 1);
  }
  await nextTick();
  updateActiveFromScroll();
});

onMounted(() => updateActiveFromScroll());

onBeforeUnmount(() => {
  cancelAnimationFrame(raf);
  if (settleTimer) window.clearTimeout(settleTimer);
});
</script>

<template>
  <div class="w-full">
    <div class="pb-2 text-md opacity-60 tracking-wide">Väntande straff</div>

    <div v-if="punishStore.loadingPending" class="px-4 pb-4">
      <span class="loading loading-spinner"></span>
    </div>

    <div v-else class="pb-2">
      <div
        ref="scroller"
        class="relative overflow-x-auto no-scrollbar scroll-smooth snap-x snap-mandatory"
        @scroll="onScroll"
        @touchend="onScrollEndLike"
        @mouseup="onScrollEndLike"
        @scrollend="onScrollEndLike"
        tabindex="0"
      >
        <ul class="flex">
          <PendingPunishmentCard
            v-for="(p, i) in items"
            :key="p.id"
            :p="p"
            :data-card-index="i"
            @confetti="playConfettiAt"
          />

          <li v-if="items.length === 0" class="opacity-60 text-sm py-2">Inga väntande straff 🎉</li>
        </ul>
      </div>

      <div v-if="showDots" class="mt-2 flex justify-center gap-2">
        <button
          v-for="(_, i) in items"
          :key="i"
          class="h-2 w-2 rounded-full transition-opacity"
          :class="i === activeIndex ? 'bg-base-content opacity-70' : 'bg-base-content opacity-30'"
          @click="scrollToIndex(i)"
          aria-label="Go to item"
        />
      </div>
    </div>

    <div v-if="punishStore.error" class="px-4 pb-4 text-sm text-error">
      {{ punishStore.error }}
    </div>
    <ConfettiBurst ref="burst" :count="180" :duration-ms="1500" z-index="z-[9999]" />
  </div>
</template>
