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

const userId = computed(() => Number(route.params.id));

async function load() {
  if (!Number.isFinite(userId.value)) return;
  await usersStore.fetchOne(userId.value);
}

onMounted(load);
watch(userId, load);

const avatarUrl = computed(() => selected.value?.avatar_url || "/kallan.svg");
const displayName = computed(() => selected.value?.username || "");
</script>

<template>
  <div class="min-h-dvh bg-base-300 flex flex-col items-center justify-center px-4 gap-8">
    <div v-if="loadingSelected" class="loading loading-spinner loading-lg"></div>

    <div v-else-if="selectedError" class="alert alert-error">
      <span>{{ selectedError }}</span>
    </div>

    <template v-else-if="selected">
      <div class="flex flex-col items-center gap-4">
        <ProfilePicture :avatarUrl="avatarUrl" />
        <h1 class="text-4xl font-bold">{{ displayName }}</h1>
      </div>

      <!-- pass the userId down so these components can query stats/punishments for that user -->
      <UserStats :userId="selected.id" />

      <LatestPunishmentsList
        :userId="selected.id"
        :title="`${selected.username}s senaste straff`"
      />
    </template>

    <div v-else class="opacity-70">User not found.</div>
  </div>
</template>
