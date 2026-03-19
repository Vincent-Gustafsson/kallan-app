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
    <!-- Overlapping avatars: initiator → confirmer (if exists) → target (red ring) -->
    <div class="flex -space-x-3 shrink-0 w-[72px]">
      <img
        :src="p.initiator.avatar_url || '/kallan.svg'"
        alt=""
        loading="lazy"
        class="size-8 rounded-full ring-2 ring-base-100 object-cover"
      />
      <img
        v-if="p.confirmer"
        :src="p.confirmer.avatar_url || '/kallan.svg'"
        alt=""
        loading="lazy"
        class="size-8 rounded-full ring-2 ring-base-100 object-cover"
      />
      <img
        :src="p.target.avatar_url || '/kallan.svg'"
        alt=""
        loading="lazy"
        class="size-8 rounded-full ring-2 ring-error object-cover"
      />
    </div>

    <!-- Main content -->
    <div class="min-w-0 flex-1">
      <div class="text-sm font-semibold truncate">{{ p.target.username }}</div>
      <div class="text-xs truncate">
        <template v-if="p.confirmer"
          ><span class="opacity-50"
            >{{ p.initiator.username }} & {{ p.confirmer.username }}</span
          ></template
        >
        <template v-else
          ><span class="opacity-50">{{ p.initiator.username }}</span>
          <span class="ml-2 badge badge-accent badge-xs align-middle">Bongsköterska</span></template
        >
      </div>
      <p v-if="p.reason?.trim()" class="text-xs opacity-60 truncate mt-0.5">{{ p.reason }}</p>
      <p v-else class="text-xs opacity-30 italic truncate mt-0.5">Ingen anledning</p>
    </div>

    <!-- Right column: date + amount -->
    <div class="flex flex-col items-end gap-1 shrink-0">
      <span class="text-xs opacity-40">{{ formatDate(p.confirmed_at!) }}</span>
      <div class="flex items-center gap-1">
        <span class="text-sm font-bold">+{{ p.amount }}</span>
        <PunishmentIcon size="size-4" color="fill-current opacity-60" />
      </div>
    </div>
  </li>
</template>
