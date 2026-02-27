<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useUsersStore } from "@/stores/users";
import type { UserMini } from "@/lib/users/usersApi";

const props = withDefaults(
  defineProps<{
    excludeMe?: boolean;
    limit?: number;
    placeholder?: string;
    autoFocus?: boolean;
  }>(),
  {
    excludeMe: true,
    limit: 20,
    placeholder: "Search users…",
    autoFocus: false,
  },
);

const emit = defineEmits<{
  (e: "select", user: UserMini): void;
}>();

const users = useUsersStore();
const q = ref("");

const inputEl = ref<HTMLInputElement | null>(null);

function initials(name: string) {
  const s = (name || "").trim();
  if (!s) return "?";
  return s.slice(0, 2).toUpperCase();
}

// tiny debounce (mobile-friendly)
let t: number | undefined;
watch(
  q,
  (val) => {
    window.clearTimeout(t);
    t = window.setTimeout(() => {
      users.fetch({ q: val, excludeMe: props.excludeMe, limit: props.limit });
    }, 200);
  },
  { immediate: false },
);

onMounted(async () => {
  await users.fetch({ q: "", excludeMe: props.excludeMe, limit: props.limit });
  if (props.autoFocus) inputEl.value?.focus();
});

const list = computed(() => users.users);

function pick(u: UserMini) {
  emit("select", u);
}
</script>

<template>
  <div class="w-full">
    <label class="input input-bordered flex items-center gap-2">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 opacity-60"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="m21 21-4.3-4.3m1.8-5.2a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z"
        />
      </svg>

      <input
        ref="inputEl"
        v-model="q"
        type="text"
        class="grow"
        :placeholder="placeholder"
        autocapitalize="none"
        autocorrect="off"
        inputmode="search"
      />

      <span v-if="users.loading" class="loading loading-spinner loading-sm"></span>
      <button v-else-if="q" class="btn btn-ghost btn-sm" type="button" @click="q = ''">
        Clear
      </button>
    </label>

    <div v-if="users.error" class="alert alert-error text-sm mt-3">
      <span>{{ users.error }}</span>
    </div>

    <div class="mt-3">
      <div v-if="users.loading && !users.ready" class="space-y-2">
        <div class="skeleton h-14 w-full"></div>
        <div class="skeleton h-14 w-full"></div>
        <div class="skeleton h-14 w-full"></div>
      </div>

      <div v-else-if="list.length === 0" class="opacity-70 p-2 text-sm">No users found.</div>

      <div v-else class="menu bg-base-100 rounded-box shadow p-2">
        <button
          v-for="u in list"
          :key="u.id"
          type="button"
          class="btn btn-ghost justify-start h-auto py-3"
          @click="pick(u)"
        >
          <div class="flex items-center gap-3 w-full">
            <div class="avatar">
              <div
                class="w-10 rounded-full overflow-hidden ring ring-base-300 ring-offset-base-100 ring-offset-2"
              >
                <img v-if="u.avatar_url" :src="u.avatar_url" alt="" />
                <div v-else class="avatar placeholder">
                  <div class="bg-neutral text-neutral-content w-10 rounded-full">
                    <span class="text-sm">{{ initials(u.username) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="min-w-0 flex-1 text-left">
              <div class="font-semibold truncate">{{ u.username }}</div>
              <div class="text-xs opacity-60">Tap to select</div>
            </div>

            <div class="badge badge-ghost">#{{ u.id }}</div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
