<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { storeToRefs } from "pinia";

import ProfilePicture from "@/components/ProfilePicture.vue";
import UserStats from "@/components/UserStats.vue";
import LatestPunishmentsList from "@/components/LatestPunishmentsList.vue";

import { useUsersStore } from "@/stores/users";

const route = useRoute();
const usersStore = useUsersStore();
const { selected, loadingSelected, selectedError } = storeToRefs(usersStore);

const userId = computed(() => {
  const n = Number(route.params.id);
  return Number.isFinite(n) ? n : undefined;
});

async function load() {
  if (!userId.value) return;
  await usersStore.fetchOne(userId.value);
}

onMounted(load);
watch(userId, load);

const avatarUrl = computed(() => selected.value?.avatar_url || "/kallan.svg");
const displayName = computed(() => selected.value?.username || "");
</script>

<template>
  <div class="min-h-dvh bg-base-300 flex flex-col items-center justify-center px-4 gap-8">

    <div v-if="selectedError" class="alert alert-error w-full max-w-sm">
      <span>{{ selectedError }}</span>
    </div>

    <template v-else>
      <!-- Profile header — skeleton while loading, real content when ready -->
      <div class="flex flex-col items-center gap-4 anim-slide-right">
        <div v-if="loadingSelected" class="avatar">
          <div class="size-30 rounded-full skeleton"></div>
        </div>
        <ProfilePicture v-else :avatarUrl="avatarUrl" />

        <div v-if="loadingSelected" class="skeleton h-10 w-36 rounded-lg"></div>
        <h1 v-else class="text-4xl font-bold capitalize">{{ displayName }}</h1>
      </div>

      <!-- Stats and list receive userId from route immediately, no waiting for selected -->
      <UserStats :userId="userId" class="anim-slide-left" />
      <LatestPunishmentsList
        :userId="userId"
        :title="selected ? `${selected.username}s senaste straff` : 'Senaste straff'"
        class="anim-slide-right"
      />
    </template>

  </div>
</template>

<style scoped>
@keyframes slide-from-left {
  from { transform: translateX(-40px); opacity: 0; }
  to   { transform: translateX(0);     opacity: 1; }
}
@keyframes slide-from-right {
  from { transform: translateX(40px);  opacity: 0; }
  to   { transform: translateX(0);     opacity: 1; }
}

.anim-slide-left  { animation: slide-from-left  0.35s ease both; }
.anim-slide-right { animation: slide-from-right 0.35s ease both 0.1s; }
</style>
