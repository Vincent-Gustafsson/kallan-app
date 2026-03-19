<script setup lang="ts">
import PunishmentIcon from "@/components/PunishmentIcon.vue";
import type { PunishmentEvent } from "@/lib/punishmentsApi";
defineProps<{ p: PunishmentEvent }>();
const formatDate = (isoDate: string) => {
  const d = new Date(isoDate);
  return new Intl.DateTimeFormat("sv-SE", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(d);
};
</script>
<template>
  <li class="list-row items-center">
    <!-- Diagonal stacked avatars (only show confirmer if exists) -->
    <div class="relative w-12 h-12 shrink-0">
      <img
        :src="p.initiator.avatar_url || '/kallan.svg'"
        alt="Avatar"
        loading="lazy"
        :class="
          p.confirmer
            ? 'w-9 h-9 rounded-full absolute top-0 left-0 ring-2 ring-base-100 object-cover'
            : 'w-9 h-9 rounded-full absolute inset-0 m-auto ring-2 ring-base-100 object-cover'
        "
      />
      <img
        v-if="p.confirmer"
        :src="p.confirmer.avatar_url || '/kallan.svg'"
        alt="Avatar"
        loading="lazy"
        class="w-9 h-9 rounded-full absolute bottom-0 right-0 ring-2 ring-base-100 object-cover"
      />
    </div>

    <!-- Main content -->
    <div class="min-w-0 flex-1">
      <div class="text-sm truncate">
        <span class="font-semibold">{{ p.initiator.username }}</span>
        <template v-if="p.confirmer">
          <span class="opacity-50"> &amp; </span>
          <span class="font-semibold">{{ p.confirmer.username }}</span>
        </template>
        <span v-else class="badge badge-accent badge-xs align-middle ml-1">Bongsköterska</span>
      </div>
      <p class="text-xs opacity-70 mt-0.5 list-col-wrap">
        <span v-if="p.reason?.trim()">{{ p.reason }}</span>
        <span v-else class="opacity-50 italic">Ingen anledning</span>
      </p>
    </div>

    <!-- Right column: date on top, icon+amount below, both end-aligned -->
    <div class="flex flex-col items-end gap-1 shrink-0">
      <span class="text-xs opacity-40">{{ formatDate(p.confirmed_at!) }}</span>
      <div class="flex items-center gap-1">
        <span class="text-sm font-bold">+{{ p.amount }}</span>
        <PunishmentIcon size="size-4" color="fill-current opacity-60" />
      </div>
    </div>
  </li>
</template>
