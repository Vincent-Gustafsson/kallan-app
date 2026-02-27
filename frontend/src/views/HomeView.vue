<script setup lang="ts">
import UserProfile from "@/components/UserProfile.vue";
import UserStats from "@/components/UserStats.vue";
import LatestPunishmentsList from "@/components/LatestPunishmentsList.vue";
import LogoutButton from "@/components/LogoutButton.vue";
import PushNotificationsPrompt from "@/components/PushNotificationsPrompt.vue";
import GiveFikapinneModal from "@/components/GiveFikapinneModal.vue";
import TakeFikapinneModal from "@/components/TakeFikapinneModal.vue";

import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const showFika = computed(() => auth.canManageFikapinnar);
</script>

<template>
  <GiveFikapinneModal />
  <TakeFikapinneModal />

  <div v-if="showFika" class="fixed top-15 left-4 flex flex-col gap-4">
    <button onclick="give_fikapinne_modal.showModal()" class="btn btn-md btn-outline">
      Ge pinne
    </button>
    <button onclick="take_fikapinne_modal.showModal()" class="btn btn-md btn-outline">
      Stryk pinne
    </button>
  </div>
  <div class="fixed top-15 right-4 z-50"><LogoutButton /></div>
  <div class="min-h-dvh bg-base-300 flex flex-col items-center justify-center px-4 gap-8">
    <PushNotificationsPrompt />

    <UserProfile />
    <UserStats />
    <LatestPunishmentsList />
  </div>
</template>
