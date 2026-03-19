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
    const r = cards[i]!.getBoundingClientRect();
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
    <p class="text-xs font-semibold opacity-50 tracking-widest uppercase mb-2 px-1">
      Föreslagna straff
    </p>

    <template v-if="punishStore.loadingPending">
      <!-- Skeleton card -->
      <div class="card bg-base-100 shadow-md rounded-box p-5 flex flex-col gap-4">
        <div class="flex items-center gap-3">
          <div class="flex -space-x-2 shrink-0">
            <div class="skeleton size-11 rounded-full"></div>
            <div class="skeleton size-11 rounded-full"></div>
          </div>
          <div class="flex-1 flex flex-col gap-1.5">
            <div class="skeleton h-4 w-36"></div>
            <div class="skeleton h-3 w-20"></div>
          </div>
          <div class="skeleton h-8 w-12 rounded-lg shrink-0"></div>
        </div>
        <div class="skeleton h-16 w-full rounded-xl"></div>
        <div class="skeleton h-10 w-full rounded-lg"></div>
      </div>
    </template>

    <template v-else>
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
        </ul>
      </div>

      <div v-if="showDots" class="mt-3 flex justify-center gap-2">
        <button
          v-for="(_, i) in items"
          :key="i"
          class="h-2 rounded-full transition-all duration-200"
          :class="
            i === activeIndex ? 'w-4 bg-primary opacity-80' : 'w-2 bg-base-content opacity-30'
          "
          @click="scrollToIndex(i)"
          aria-label="Go to item"
        />
      </div>
    </template>

    <div v-if="punishStore.error" class="text-sm text-error mt-2 px-1">
      {{ punishStore.error }}
    </div>
    <ConfettiBurst ref="burst" :count="180" :duration-ms="1500" z-index="z-[9999]" />
  </div>
</template>
