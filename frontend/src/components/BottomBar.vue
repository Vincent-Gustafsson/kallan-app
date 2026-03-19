<script setup lang="ts">
import { RouterLink } from "vue-router";
import PunishmentIcon from "./PunishmentIcon.vue";
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
          viewBox="0 0 512 512"
          fill="currentColor"
          class="size-6"
        >
          <!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.-->
          <path
            d="M277.8 8.6c-12.3-11.4-31.3-11.4-43.5 0l-224 208c-9.6 9-12.8 22.9-8 35.1S18.8 272 32 272l16 0 0 176c0 35.3 28.7 64 64 64l288 0c35.3 0 64-28.7 64-64l0-176 16 0c13.2 0 25-8.1 29.8-20.3s1.6-26.2-8-35.1l-224-208zM240 320l32 0c26.5 0 48 21.5 48 48l0 96-128 0 0-96c0-26.5 21.5-48 48-48z"
          />
        </svg>
      </button>
    </RouterLink>

    <RouterLink :to="{ name: 'work' }" custom v-slot="{ navigate, isActive }">
      <button
        @click="navigate"
        :class="isActive ? 'dock-active after:bg-primary' : ''"
        :aria-current="isActive ? 'page' : undefined"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 512 512"
          fill="currentColor"
          class="size-6"
        >
          <path
            d="M200 48l112 0c4.4 0 8 3.6 8 8l0 40-128 0 0-40c0-4.4 3.6-8 8-8zm-56 8l0 40-80 0C28.7 96 0 124.7 0 160l0 96 512 0 0-96c0-35.3-28.7-64-64-64l-80 0 0-40c0-30.9-25.1-56-56-56L200 0c-30.9 0-56 25.1-56 56zM512 304l-192 0 0 16c0 17.7-14.3 32-32 32l-64 0c-17.7 0-32-14.3-32-32l0-16-192 0 0 112c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-112z"
          />
        </svg>
      </button>
    </RouterLink>

    <RouterLink :to="{ name: 'create-event' }" custom v-slot="{ navigate, isActive }">
      <button
        @click="navigate"
        :class="isActive ? 'dock-active after:bg-primary' : ''"
        :aria-current="isActive ? 'page' : undefined"
      >
        <PunishmentIcon size="size-6" />
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
  </div>
</template>
