<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useUsersStore } from "@/stores/users";

const router = useRouter();

const usersStore = useUsersStore();
const { users, loading, error, ready } = storeToRefs(usersStore);

const fallbackAvatar = "/kallan.svg";

onMounted(() => {
  // Avoid refetching if your store already loaded once
  if (!ready.value && !loading.value) usersStore.fetch({ excludeMe: true });
});

function openUser(id: number) {
  router.push({ name: "user", params: { id } });
}
</script>

<template>
  <div class="min-h-dvh bg-base-300 px-4 py-20">
    <div class="max-w-6xl mx-auto">
      <div class="grid grid-cols-2 gap-3 place-items-stretch">
        <button
          v-for="user in users"
          :key="user.id"
          type="button"
          class="card bg-base-100 shadow w-full justify-self-stretch appearance-none"
          @click="openUser(user.id)"
        >
          <div class="card-body p-3 flex flex-col items-center justify-center gap-2 w-full">
            <div class="avatar">
              <div
                class="ring-primary ring-offset-base-100 size-12 rounded-full ring-2 ring-offset-2 overflow-hidden"
              >
                <img
                  class="block w-full h-full object-cover"
                  :src="user.avatar_url || fallbackAvatar"
                  alt="Avatar"
                  loading="lazy"
                />
              </div>
            </div>

            <div class="text-xl font-medium w-full break-words">
              {{ user.username }}
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
