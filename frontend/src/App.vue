<script setup lang="ts">
import { RouterView, useRoute } from "vue-router";
import BottomBar from "@/components/BottomBar.vue";

const route = useRoute();
</script>

<template>
  <div class="min-h-dvh bg-base-300">
    <RouterView />
  </div>
  <BottomBar v-if="!route.meta.hideBottomBar" />
</template>
