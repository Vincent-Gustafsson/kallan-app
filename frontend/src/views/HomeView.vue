<script setup lang="ts">
import UserProfile from "@/components/UserProfile.vue";
import UserStats from "@/components/UserStats.vue";
import LatestPunishmentsList from "@/components/LatestPunishmentsList.vue";
import SettingsButton from "@/components/SettingsButton.vue";
import PushNotificationsPrompt from "@/components/PushNotificationsPrompt.vue";
import GiveFikapinneModal from "@/components/GiveFikapinneModal.vue";
import TakeFikapinneModal from "@/components/TakeFikapinneModal.vue";

import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const showFika = computed(() => auth.canManageFikapinnar);
</script>

<template>
  <div>
    <!--<GiveFikapinneModal />
    <TakeFikapinneModal />
    <div v-if="showFika" class="fixed top-15 left-4 flex flex-col gap-4">
      <button onclick="give_fikapinne_modal.showModal()" class="btn btn-md btn-outline">
        Ge pinne
      </button>
      <button onclick="take_fikapinne_modal.showModal()" class="btn btn-md btn-outline">
        Stryk pinne
      </button>
    </div> -->
    <div class="fixed top-15 right-4 z-50"><SettingsButton /></div>
    <div class="min-h-dvh bg-base-300 flex flex-col items-center justify-center px-4 gap-8">
      <PushNotificationsPrompt />

      <UserProfile />
      <UserStats class="anim-slide-left" />
      <LatestPunishmentsList class="anim-slide-right" />
    </div>
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
