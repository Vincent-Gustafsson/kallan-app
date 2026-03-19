<script setup lang="ts">
import { computed, onMounted, watch, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { usePunishmentsStore } from "@/stores/punishments";
import AllPunishmentsModal from "@/components/AllPunishmentsModal.vue";
import PunishmentListRow from "@/components/PunishmentListRow.vue";

const props = defineProps<{
  userId?: number;
  title?: string;
}>();

const auth = useAuthStore();
const punish = usePunishmentsStore();

const LIMIT = 3;

const effectiveUserId = computed(() => props.userId ?? auth.user?.id ?? null);
const items = computed(() => punish.confirmed ?? []);
const fillerCount = computed(() => Math.max(0, LIMIT - items.value.length));

function fetchForUser() {
  if (!effectiveUserId.value) return;
  punish.fetchConfirmed({ target_id: effectiveUserId.value, limit: LIMIT });
}

onMounted(fetchForUser);
watch(effectiveUserId, (id) => {
  if (id) fetchForUser();
});

const headerText = computed(() => {
  if (props.title) return props.title;
  return props.userId ? "Senaste straffen" : "Dina senaste straff";
});

const canOpenAll = computed(() => !punish.loadingConfirmed && items.value.length > 0);

const allModal = ref<InstanceType<typeof AllPunishmentsModal> | null>(null);
function openAll() {
  if (!canOpenAll.value) return;
  allModal.value?.open();
}
</script>

<template>
  <div class="w-full">
    <!-- modal lives here so it knows which userId/title to use -->
    <AllPunishmentsModal ref="allModal" :userId="effectiveUserId ?? undefined" />

    <ul class="list bg-base-100 w-full rounded-box shadow-md overflow-hidden">
      <div class="flex items-center justify-between p-4 pb-2">
        <li class="text-xs opacity-60 tracking-wide">
          {{ headerText }}
        </li>

        <button class="btn btn-sm btn-outline" :disabled="!canOpenAll" @click="allModal?.open()">
          Alla straff
        </button>
      </div>

      <template v-if="punish.loadingConfirmed">
        <li v-for="i in LIMIT" :key="'sk-' + i" class="list-row items-center">
          <div class="relative w-12 h-12 shrink-0">
            <div class="skeleton size-9 rounded-full absolute top-0 left-0"></div>
            <div class="skeleton size-9 rounded-full absolute bottom-0 right-0"></div>
          </div>

          <div class="min-w-0 flex-1 flex flex-col gap-1">
            <div class="skeleton h-4 w-40"></div>
            <div class="skeleton h-3 w-28"></div>
          </div>

          <div class="flex flex-col items-end gap-1 shrink-0">
            <div class="skeleton h-3 w-16 rounded"></div>
            <div class="skeleton h-4 w-10 rounded"></div>
          </div>
        </li>
      </template>

      <template v-else>
        <PunishmentListRow
          v-for="(p, idx) in items"
          :key="p.id"
          :p="p"
          class="punch-row"
          :style="{ '--delay': `${idx * 0.06}s` }"
        />

        <li
          v-for="i in fillerCount"
          :key="'fill-' + i"
          class="list-row items-center invisible pointer-events-none"
          aria-hidden="true"
        >
          <div class="relative w-12 h-12 shrink-0"></div>
          <div class="min-w-0 flex-1 flex flex-col gap-1">
            <div class="h-4 w-40"></div>
            <div class="h-3 w-28"></div>
          </div>
          <div class="flex flex-col items-end gap-1 shrink-0">
            <div class="h-3 w-16"></div>
            <div class="h-4 w-10"></div>
          </div>
        </li>
      </template>
    </ul>
  </div>
</template>

<style scoped>
@keyframes slide-in-left {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

:deep(.punch-row) {
  animation: slide-in-left 0.3s ease both;
  animation-delay: var(--delay, 0s);
}
</style>
