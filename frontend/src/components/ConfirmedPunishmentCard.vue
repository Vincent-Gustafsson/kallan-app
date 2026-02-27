<script setup lang="ts">
import ProfilePicture from "@/components/ProfilePicture.vue";
import type { PunishmentEvent } from "@/lib/punishmentsApi";

const props = defineProps<{ p: PunishmentEvent }>();

const formatConfirmedAt = (isoDate: string) => {
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
    <div class="col-span-full w-full flex flex-col">
      <!-- Top row -->
      <div class="flex">
        <!-- Left group: avatars + text -->
        <div class="flex items-center gap-3 min-w-0">
          <div class="flex items-center -space-x-2 shrink-0">
            <ProfilePicture sizeClass="size-8" :avatarUrl="p.initiator.avatar_url!" />
            <ProfilePicture sizeClass="size-8" :avatarUrl="p.confirmer!.avatar_url!" />
            <ProfilePicture
              sizeClass="size-8"
              ringColorClass="ring-error"
              :avatarUrl="p.target.avatar_url!"
            />
          </div>

          <div class="min-w-0">
            <div class="truncate">
              {{ p.initiator.username }}
              <span class="opacity-60 font-normal">&</span>
              {{ p.confirmer!.username }}
              <span class="opacity-60 font-normal">→</span>
              {{ p.target.username }}
            </div>

            <div class="text-xs opacity-60 truncate">
              {{ formatConfirmedAt(p.confirmed_at!) }}
            </div>
          </div>
        </div>

        <!-- Right: badge -->
        <div class="badge badge-neutral ml-auto shrink-0">
          {{ p.amount }}
        </div>
      </div>

      <!-- Bottom row (full width, its own line) -->
      <div class="mt-4">
        <div class="text-sm font-semibold opacity-70 mb-2">Anledning</div>
        <div class="text-sm whitespace-pre-wrap">
          {{ p.reason || "-" }}
        </div>
      </div>
    </div>
  </li>
</template>
