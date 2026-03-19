<script setup lang="ts">
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import ChangePfpButton from "@/components/ChangePfpButton.vue";
import ProfilePicture from "@/components/ProfilePicture.vue";

const auth = useAuthStore();

const avatarUrl = computed(() => auth.user?.avatar_url ?? "/kallan.svg");

const displayName = computed(() => {
  const u = auth.user?.username ?? "";
  return u ? u[0]!.toUpperCase() + u.slice(1) : "";
});
</script>

<template>
  <div class="flex flex-col items-center gap-4 anim-slide-right">
    <div class="indicator">
      <div class="indicator-item indicator-top">
        <ChangePfpButton />
      </div>
      <ProfilePicture :avatarUrl="avatarUrl" />
    </div>

    <h1 class="text-4xl font-bold">{{ displayName }}</h1>
  </div>
</template>

<style scoped>
@keyframes slide-from-right {
  from { transform: translateX(40px); opacity: 0; }
  to   { transform: translateX(0);    opacity: 1; }
}

.anim-slide-right {
  animation: slide-from-right 0.35s ease both;
}
</style>
