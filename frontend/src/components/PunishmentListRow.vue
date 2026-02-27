<script setup lang="ts">
import ProfilePicture from "@/components/ProfilePicture.vue";
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
  <li class="list-row">
    <div class="avatar-group -space-x-6">
      <div class="avatar size-14">
        <img :src="p.initiator.avatar_url!" alt="Avatar" loading="lazy" />
      </div>
      <div class="avatar size-14">
        <img :src="p.confirmer!.avatar_url!" alt="Avatar" loading="lazy" />
      </div>
    </div>

    <div class="min-w-0">
      <div>
        <div class="truncate">{{ p.initiator.username }} & {{ p.confirmer?.username ?? "?" }}</div>
        <div class="text-xs uppercase font-semibold opacity-60">Anledning</div>
      </div>

      <p class="list-col-wrap text-xs">
        <span v-if="p.reason?.trim()">{{ p.reason }}</span>
        <span v-else class="opacity-60">Ingen anledning</span>
      </p>
    </div>

    <div class="flex flex-col items-end gap-2">
      <span class="text-xs opacity-60">{{ formatDate(p.confirmed_at!) }}</span>
      <div class="badge badge-neutral">+{{ p.amount }}</div>
    </div>
  </li>
</template>
