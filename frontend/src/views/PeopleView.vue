<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useUsersStore } from "@/stores/users";
import PunishmentIcon from "@/components/PunishmentIcon.vue";
import ProfilePicture from "@/components/ProfilePicture.vue";

const router = useRouter();
const usersStore = useUsersStore();
const { users, loading, error, ready } = storeToRefs(usersStore);

const fallbackAvatar = "/kallan.svg";

onMounted(() => {
  if (!ready.value && !loading.value) usersStore.fetch({ excludeMe: true, limit: 50 });
});

function openUser(id: number) {
  router.push({ name: "user", params: { id } });
}

const TIER_GROUPS = [
  { tier: "vest", title: "Västar" },
  { tier: "hat", title: "Hattar" },
  { tier: "bandana", title: "Provisar" },
] as const;

const groups = computed(() => {
  let offset = 0;
  return TIER_GROUPS.map((g) => {
    const groupUsers = users.value
      .filter((u) => u.tier === g.tier)
      .sort((a, b) => (b.punishment_count ?? 0) - (a.punishment_count ?? 0));
    const startIndex = offset;
    offset += groupUsers.length;
    return { ...g, users: groupUsers, startIndex };
  }).filter((g) => g.users.length > 0);
});
</script>

<template>
  <div class="min-h-dvh bg-base-300 px-4 pt-16 pb-24">
    <div class="flex flex-col gap-6 max-w-lg mx-auto">
      <!-- Error -->
      <div v-if="error" class="text-sm text-error text-center mt-8">{{ error }}</div>

      <!-- Loading skeletons -->
      <template v-if="loading">
        <div v-for="i in 2" :key="i">
          <div class="skeleton h-4 w-24 mb-2 rounded"></div>
          <ul class="list bg-base-100 rounded-box shadow">
            <li v-for="j in 3" :key="j" class="list-row">
              <div class="skeleton size-10 rounded-full shrink-0"></div>
              <div class="flex-1 flex flex-col gap-2">
                <div class="skeleton h-4 w-28"></div>
              </div>
              <div class="flex items-center gap-3">
                <div class="skeleton h-4 w-8 rounded"></div>
                <div class="skeleton h-4 w-8 rounded"></div>
              </div>
            </li>
          </ul>
        </div>
      </template>

      <!-- Grouped lists -->
      <template v-else>
        <div v-for="group in groups" :key="group.tier">
          <p class="text-xs font-semibold opacity-50 tracking-widest uppercase mb-2 px-1">
            {{ group.title }}
          </p>
          <ul class="list bg-base-100 rounded-box shadow overflow-hidden">
            <li
              v-for="(user, idx) in group.users"
              :key="user.id"
              class="list-row cursor-pointer user-row"
              :style="{ '--delay': `${(group.startIndex + idx) * 0.06}s` }"
              @click="openUser(user.id)"
            >
              <ProfilePicture sizeClass="size-10" :avatarUrl="user.avatar_url || '/kallan.svg'" />

              <div class="flex-1 min-w-0 flex items-center">
                <span style="font-size: 1rem" class="font-semibold truncate capitalize">{{
                  user.username
                }}</span>
              </div>

              <div class="flex items-center gap-3 shrink-0 text-base-content/70">
                <div class="flex items-center gap-1">
                  <span class="font-semibold tabular-nums">{{ user.punishment_count ?? 0 }}</span>
                  <PunishmentIcon size="size-4" class="text-secondary" />
                </div>
                <div class="flex items-center gap-1">
                  <span class="font-semibold tabular-nums">{{ user.fikapinne_count ?? 0 }}</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 384 512"
                    class="size-4 fill-current text-secondary"
                  >
                    <path
                      d="M335.1 160c.6-5.3 .9-10.6 .9-16 0-79.5-64.5-144-144-144S48 64.5 48 144c0 5.4 .3 10.7 .9 16l-.9 0c-26.5 0-48 21.5-48 48s21.5 48 48 48l288 0c26.5 0 48-21.5 48-48s-21.5-48-48-48l-.9 0zM64 304L169.2 529.5c4.1 8.8 13 14.5 22.8 14.5s18.6-5.7 22.8-14.5L320 304 64 304z"
                    />
                  </svg>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
@keyframes slide-in-right {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.user-row {
  animation: slide-in-right 0.3s ease both;
  animation-delay: var(--delay, 0s);
}
</style>
