<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import ProfilePicture from "@/components/ProfilePicture.vue";
import { apiListConfirmedPunishmentEvents, type PunishmentEvent } from "@/lib/punishmentsApi";

import PunishmentListRow from "@/components/PunishmentListRow.vue";

const props = defineProps<{
  userId?: number;
  modalId?: string;
}>();

const auth = useAuthStore();
const dialogRef = ref<HTMLDialogElement | null>(null);

const effectiveUserId = computed(() => props.userId ?? auth.user?.id ?? null);

const items = ref<PunishmentEvent[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

const SKELETON_ROWS = 10;

async function fetchAll() {
  if (!effectiveUserId.value) return;

  loading.value = true;
  error.value = null;

  try {
    items.value = await apiListConfirmedPunishmentEvents({
      target_id: effectiveUserId.value,
      // no limit => all
    });
  } catch (e) {
    items.value = [];
    error.value = e instanceof Error ? e.message : "Kunde inte ladda straff";
  } finally {
    loading.value = false;
  }
}

function open() {
  fetchAll();
  dialogRef.value?.showModal();
}

function close() {
  dialogRef.value?.close();
}

watch(effectiveUserId, () => {
  // if the modal is open and you navigate to another profile, update live
  if (dialogRef.value?.open) fetchAll();
});

defineExpose({ open, close });
</script>

<template>
  <dialog
    ref="dialogRef"
    :id="modalId || 'all_punishments_modal'"
    class="modal"
    @cancel.prevent="close"
  >
    <div class="modal-box w-11/12 max-w-2xl p-0 overflow-hidden">
      <!-- header -->
      <div class="p-4 border-b border-base-200 flex items-center justify-between">
        <div class="text-lg font-semibold">Alla straff</div>
        <button class="btn btn-sm" type="button" @click="close">Stäng</button>
      </div>

      <!-- body -->
      <div class="max-h-[70dvh] overflow-y-auto">
        <ul class="list bg-base-100 w-full">
          <template v-if="loading">
            <li v-for="i in SKELETON_ROWS" :key="'sk-' + i" class="list-row">
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
            <li v-if="error" class="p-4">
              <div class="alert alert-error">
                <span>{{ error }}</span>
              </div>
            </li>

            <li v-else-if="items.length === 0" class="p-4 text-sm opacity-60">Inga straff än 🎉</li>

            <PunishmentListRow v-else v-for="p in items" :key="p.id" :p="p" />
          </template>
        </ul>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button aria-label="close" @click="close">close</button>
    </form>
  </dialog>
</template>
