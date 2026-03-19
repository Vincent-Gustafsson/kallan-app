<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from "vue";
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

// ── Countdown ─────────────────────────────────────────────────────────────────

const EXPIRE_SECONDS = 300;

function secondsLeft() {
  const created = new Date(props.p.created_at).getTime();
  const remaining = Math.max(0, EXPIRE_SECONDS - Math.floor((Date.now() - created) / 1000));
  return remaining;
}

const countdown = ref(secondsLeft());

const countdownLabel = computed(() => {
  const s = countdown.value;
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${String(sec).padStart(2, "0")}`;
});

const countdownUrgent = computed(() => countdown.value <= 60);

let timer: ReturnType<typeof setInterval> | null = null;

onMounted(() => {
  timer = setInterval(() => {
    countdown.value = secondsLeft();
    if (countdown.value === 0 && timer) clearInterval(timer);
  }, 1000);
});

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});

</script>

<template>
  <li class="card bg-base-100 shadow-md rounded-box shrink-0 w-full min-w-0 snap-start">
    <div class="card-body gap-4 p-5">

      <!-- Header: avatars + names + amount -->
      <div class="flex items-center gap-3">
        <div class="flex items-center -space-x-3 shrink-0">
          <ProfilePicture
            sizeClass="size-11"
            :avatarUrl="p.initiator.avatar_url || '/kallan.svg'"
          />
          <ProfilePicture
            sizeClass="size-11"
            ringColorClass="ring-error"
            :avatarUrl="p.target.avatar_url || '/kallan.svg'"
          />
        </div>

        <div class="flex-1 min-w-0">
          <div class="text-sm font-semibold truncate">
            {{ p.initiator.username }}
            <span class="opacity-40 font-normal mx-0.5">→</span>
            {{ p.target.username }}
          </div>
          <div class="flex items-center gap-1 text-xs">
            <span class="opacity-50">{{ formatCreatedAt(p.created_at) }}</span>
            <span class="opacity-30">·</span>
            <span :class="countdownUrgent ? 'text-error font-semibold' : 'opacity-50'">
              {{ countdownLabel }}
            </span>
          </div>
        </div>

        <div class="text-3xl font-bold text-primary shrink-0">+{{ p.amount }}</div>
      </div>

      <!-- Reason -->
      <div class="bg-base-200/60 rounded-xl px-4 py-3 text-sm min-h-12">
        <span v-if="p.reason?.trim()">{{ p.reason }}</span>
        <span v-else class="opacity-50 italic">Ingen anledning angiven</span>
      </div>

      <!-- Action -->
      <button
        v-if="isMine"
        class="btn btn-outline btn-error btn-md w-full"
        :disabled="undoing"
        type="button"
        @click.prevent="onUndo"
      >
        <span v-if="undoing" class="loading loading-spinner loading-xs"></span>
        <span v-else>Ångra</span>
      </button>

      <button
        v-else
        class="btn btn-primary btn-md w-full"
        :disabled="!canJoin || joining"
        type="button"
        style="touch-action: manipulation"
        @pointerup.prevent="onJoin"
        @touchend.prevent="onJoin"
      >
        <span v-if="joining" class="loading loading-spinner loading-xs"></span>
        <span v-else>Gå med</span>
      </button>

    </div>
  </li>
</template>
