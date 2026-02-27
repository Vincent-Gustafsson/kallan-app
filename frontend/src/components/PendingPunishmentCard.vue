<script setup lang="ts">
import { computed, ref } from "vue";
import ProfilePicture from "@/components/ProfilePicture.vue";
import { useAuthStore } from "@/stores/auth";
import { usePunishmentsStore } from "@/stores/punishments";
import type { PunishmentEvent } from "@/lib/punishmentsApi";

const props = defineProps<{ p: PunishmentEvent }>();

const emit = defineEmits<{
  (e: "confetti", x: number, y: number): void;
}>();

const authStore = useAuthStore();
const punishStore = usePunishmentsStore();

const joining = ref(false);

const canJoin = computed(() => {
  const me = authStore.user;
  if (!me) return false;

  if (me.tier === "bandana") return false;
  if (props.p.target.id === me.id) return false;
  if (props.p.initiator.id === me.id) return false;
  if (props.p.initiator.tier === "hat" && me.tier === "hat") return false;

  return true;
});

function getPoint(e: MouseEvent | TouchEvent | PointerEvent) {
  if ("changedTouches" in e && e.changedTouches?.length) {
    return { x: e.changedTouches[0]!.clientX, y: e.changedTouches[0]!.clientY };
  }
  const me = e as MouseEvent;
  return { x: me.clientX, y: me.clientY };
}

async function onJoin(e: MouseEvent | TouchEvent | PointerEvent) {
  if (!canJoin.value || joining.value) return;

  const { x, y } = getPoint(e);

  joining.value = true;
  try {
    emit("confetti", x, y);
    await punishStore.confirmEvent(props.p.id);
  } finally {
    joining.value = false;
  }
}

const formatCreatedAt = (isoDate: string) => {
  const d = new Date(isoDate);
  return new Intl.DateTimeFormat("sv-SE", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(d);
};

const isMine = computed(() => authStore.user?.id === props.p.initiator.id);

const undoing = ref(false);

async function onUndo() {
  if (!isMine.value || undoing.value) return;
  undoing.value = true;
  try {
    await punishStore.deleteEvent(props.p.id);
  } finally {
    undoing.value = false;
  }
}
</script>

<template>
  <li
    class="card bg-base-100 border border-base-200 rounded-box shadow-sm shrink-0 w-full snap-start"
  >
    <div class="card-body min-w-0">
      <div class="flex justify-between gap-3">
        <div class="flex items-center -space-x-2">
          <ProfilePicture sizeClass="w-12 h-12" :avatarUrl="p.initiator.avatar_url!" />
          <ProfilePicture
            sizeClass="w-12 h-12"
            ringColorClass="ring-error"
            :avatarUrl="p.target.avatar_url!"
          />
        </div>

        <div class="flex flex-col items-end">
          <span class="opacity-60">{{ formatCreatedAt(p.created_at) }}</span>
          <div class="stats">
            <div class="stat-value">+{{ p.amount }}</div>
          </div>
        </div>
      </div>

      <div>
        <div class="text-sm font-semibold mt-2">
          {{ p.initiator.username }} vill ge {{ p.target.username }} <br />
        </div>

        <div class="text-sm font-semibold opacity-70 mt-4 mb-2">Anledning</div>

        <div class="flex">
          <div
            class="bg-base-200/60 w-full rounded-box p-4 text-sm leading-relaxed whitespace-pre-wrap"
          >
            <span v-if="p.reason?.trim()">{{ p.reason }}</span>
            <span v-else class="opacity-60">Ingen anledning angiven</span>
          </div>
        </div>
      </div>

      <button
        v-if="isMine"
        class="btn btn-error btn-md w-full mt-2"
        :disabled="undoing"
        @click.prevent="onUndo"
        type="button"
      >
        <span v-if="undoing" class="loading loading-spinner loading-xs"></span>
        <span v-else>Ångra</span>
      </button>

      <button
        v-else
        class="btn btn-primary btn-md w-full mt-2"
        :disabled="!canJoin || joining"
        @pointerup.prevent="onJoin"
        @touchend.prevent="onJoin"
        style="touch-action: manipulation"
        type="button"
      >
        <span v-if="joining" class="loading loading-spinner loading-xs"></span>
        <span v-else>Gå med</span>
      </button>
    </div>
  </li>
</template>
