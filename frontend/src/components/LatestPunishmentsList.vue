<script setup lang="ts">
import { computed, onMounted, watch, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { usePunishmentsStore } from "@/stores/punishments";
import ProfilePicture from "@/components/ProfilePicture.vue";
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

    <ul class="list bg-base-100 w-full rounded-box shadow-md">
      <div class="flex items-center justify-between p-4 pb-2">
        <li class="text-xs opacity-60 tracking-wide">
          {{ headerText }}
        </li>

        <button class="btn btn-sm btn-outline" :disabled="!canOpenAll" @click="allModal?.open()">
          Alla straff
        </button>
      </div>

      <template v-if="punish.loadingConfirmed">
        <li v-for="i in LIMIT" :key="'sk-' + i" class="list-row">
          <div class="avatar-group -space-x-6">
            <div class="avatar"><div class="size-12 bg-base-200 rounded-box"></div></div>
            <div class="avatar"><div class="size-12 bg-base-200 rounded-box"></div></div>
          </div>

          <div class="min-w-0">
            <div class="h-4 w-40 bg-base-200 rounded mb-2"></div>
            <div class="h-3 w-28 bg-base-200 rounded mb-2"></div>
            <div class="h-3 w-56 bg-base-200 rounded"></div>
          </div>

          <div class="badge badge-neutral opacity-30">+?</div>
        </li>
      </template>

      <template v-else>
        <PunishmentListRow v-for="p in items" :key="p.id" :p="p" />

        <li
          v-for="i in fillerCount"
          :key="'fill-' + i"
          class="list-row opacity-0 pointer-events-none"
          aria-hidden="true"
        >
          <div class="h-12"></div>
          <div><div class="h-4 w-24 bg-base-200 rounded"></div></div>
        </li>
      </template>
    </ul>
  </div>
</template>
