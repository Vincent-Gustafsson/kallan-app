<script setup lang="ts">
import { RouterLink } from "vue-router";
</script>

<template>
  <div class="dock dock-sm" style="bottom: calc(1rem - env(safe-area-inset-bottom))">
    <RouterLink :to="{ name: 'punishments' }" custom v-slot="{ navigate, isActive }">
      <button
        @click="navigate"
        :class="isActive ? 'dock-active after:bg-primary' : ''"
        :aria-current="isActive ? 'page' : undefined"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 320 512"
          fill="currentColor"
          class="size-6"
        >
          <path
            d="M32.6 25.7C35.6 10.8 48.7 0 64 0L256 0c15.3 0 28.4 10.8 31.4 25.7L316.8 173c2.1 10.5 3.2 21.2 3.2 32l0 3c0 77.4-55 142-128 156.8l0 115.2 64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L64 544c-17.7 0-32-14.3-32-32s14.3-32 32-32l64 0 0-115.2C55 350 0 285.4 0 208l0-3c0-10.7 1.1-21.4 3.2-32L32.6 25.7zM77.4 128l165.1 0-12.8-64-139.5 0-12.8 64z"
          />
        </svg>
      </button>
    </RouterLink>

    <RouterLink :to="{ name: 'home' }" custom v-slot="{ navigate, isActive }">
      <button
        @click="navigate"
        :class="isActive ? 'dock-active after:bg-primary' : ''"
        :aria-current="isActive ? 'page' : undefined"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 448 512"
          fill="currentColor"
          class="size-6"
        >
          <path
            d="M224 248a120 120 0 1 0 0-240 120 120 0 1 0 0 240zm-29.7 56C95.8 304 16 383.8 16 482.3 16 498.7 29.3 512 45.7 512l356.6 0c16.4 0 29.7-13.3 29.7-29.7 0-98.5-79.8-178.3-178.3-178.3l-59.4 0z"
          />
        </svg>
      </button>
    </RouterLink>

    <RouterLink :to="{ name: 'users' }" custom v-slot="{ navigate, isActive }">
      <button
        @click="navigate"
        :class="isActive ? 'dock-active after:bg-primary' : ''"
        :aria-current="isActive ? 'page' : undefined"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 576 512"
          fill="currentColor"
          class="size-6"
        >
          <!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.-->
          <path
            d="M64 128a112 112 0 1 1 224 0 112 112 0 1 1 -224 0zM0 464c0-97.2 78.8-176 176-176s176 78.8 176 176l0 6c0 23.2-18.8 42-42 42L42 512c-23.2 0-42-18.8-42-42l0-6zM432 64a96 96 0 1 1 0 192 96 96 0 1 1 0-192zm0 240c79.5 0 144 64.5 144 144l0 22.4c0 23-18.6 41.6-41.6 41.6l-144.8 0c6.6-12.5 10.4-26.8 10.4-42l0-6c0-51.5-17.4-98.9-46.5-136.7 22.6-14.7 49.6-23.3 78.5-23.3z"
          />
        </svg>
      </button>
    </RouterLink>
  </div>
</template>
