<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useUsersStore } from "@/stores/users";
import { usePunishmentsStore } from "@/stores/punishments";
import { useAuthStore } from "@/stores/auth";
import ProfilePicture from "@/components/ProfilePicture.vue";
import AvatarRain from "@/components/AvatarRain.vue";

const router = useRouter();
const usersStore = useUsersStore();
const punishStore = usePunishmentsStore();
const authStore = useAuthStore();

const fallbackAvatar = "/kallan.svg";
const MAX_REASON = 50;
const MIN_POINTS = 1;
const MAX_POINTS = 10;

const showTake = computed(() => authStore.user?.tier === "vest");
const canGive = computed(() => authStore.myTier !== "bandana");

const avatarUrls = computed(() =>
  usersStore.users.map((u) => u.avatar_url).filter((url): url is string => !!url),
);

type Mode = "give" | "take";
const mode = ref<Mode>("give");

function setMode(m: Mode) {
  if (mode.value === m) return;
  mode.value = m;
  resetForm();
}

// ── Form state ────────────────────────────────────────────────────────────────

const selectedUserId = ref<number | null>(null);
const reason = ref("");
const points = ref(1);
const submitting = ref(false);
const submitError = ref<string | null>(null);
const dropdownRef = ref<HTMLDetailsElement | null>(null);
const dropdownTakeRef = ref<HTMLDetailsElement | null>(null);

const selectedUser = computed(
  () => usersStore.users.find((u) => u.id === selectedUserId.value) ?? null,
);

function selectUser(id: number) {
  selectedUserId.value = id;
  if (dropdownRef.value) dropdownRef.value.open = false;
  if (dropdownTakeRef.value) dropdownTakeRef.value.open = false;
}

function resetForm() {
  selectedUserId.value = null;
  reason.value = "";
  points.value = 1;
  submitting.value = false;
  submitError.value = null;
  if (dropdownRef.value) dropdownRef.value.open = false;
  if (dropdownTakeRef.value) dropdownTakeRef.value.open = false;
}

function dec() {
  if (points.value > MIN_POINTS) points.value--;
}
function inc() {
  if (points.value < MAX_POINTS) points.value++;
}

const canSubmit = computed(
  () => selectedUserId.value !== null && reason.value.length <= MAX_REASON,
);

// ── Submit ────────────────────────────────────────────────────────────────────

async function submit() {
  submitError.value = null;
  if (!selectedUserId.value) return;
  submitting.value = true;
  try {
    if (mode.value === "give") {
      await punishStore.createEvent({
        target_id: selectedUserId.value,
        amount: points.value,
        reason: reason.value.trim() || "",
      });
    } else {
      await punishStore.takeEvent({
        target_id: selectedUserId.value,
        amount: points.value,
      });
    }
    router.push({ name: "punishments" });
  } catch (e) {
    submitError.value = e instanceof Error ? e.message : "Något gick fel";
    submitting.value = false;
  }
}
</script>

<template>
  <AvatarRain v-if="avatarUrls.length" :avatarUrls="avatarUrls" zIndex="z-0" />
  <div class="min-h-dvh flex flex-col items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <!-- Vest users: two tabs -->
      <div v-if="showTake" class="tabs tabs-xl tabs-border justify-center anim-slide-left">
        <!-- Tab: Ge straff -->
        <input
          type="radio"
          name="create-tabs"
          class="tab"
          aria-label="Ge straff"
          :checked="mode === 'give'"
          @change="setMode('give')"
        />
        <div class="tab-content">
          <div class="card bg-base-100 shadow-md mt-4 anim-slide-right">
            <form class="card-body gap-5" @submit.prevent="submit">
              <!-- User dropdown + Amount picker -->
              <div class="flex gap-3 items-end">
                <div class="flex flex-col gap-1 flex-1 min-w-0">
                  <label class="text-sm font-semibold opacity-70">Till vem?</label>
                  <details ref="dropdownRef" class="dropdown w-full">
                    <summary
                      class="btn btn-lg w-full justify-start font-normal gap-3 [&::-webkit-details-marker]:hidden"
                    >
                      <template v-if="selectedUser">
                        <div class="avatar">
                          <div class="size-7 rounded-full overflow-hidden">
                            <img :src="selectedUser.avatar_url || fallbackAvatar" alt="" />
                          </div>
                        </div>
                        <span class="truncate">{{ selectedUser.username }}</span>
                      </template>
                      <span v-else class="opacity-50">Välj person...</span>
                    </summary>
                    <ul
                      class="dropdown-content bg-base-100 rounded-box z-50 w-full shadow-lg max-h-64 overflow-y-auto p-1 mt-1 flex flex-col gap-0.5"
                    >
                      <li v-if="usersStore.loading" class="flex items-center gap-2 px-3 py-2">
                        <span class="loading loading-spinner loading-sm"></span>
                        <span class="text-sm opacity-70">Laddar...</span>
                      </li>
                      <li v-for="user in usersStore.users" :key="user.id">
                        <button
                          type="button"
                          class="btn btn-ghost w-full justify-start gap-3 font-normal"
                          :class="{ 'btn-active': selectedUserId === user.id }"
                          @click="selectUser(user.id)"
                        >
                          <div class="avatar">
                            <div class="size-7 rounded-full overflow-hidden">
                              <img :src="user.avatar_url || fallbackAvatar" alt="" loading="lazy" />
                            </div>
                          </div>
                          {{ user.username }}
                        </button>
                      </li>
                    </ul>
                  </details>
                  <div v-if="usersStore.error" class="text-sm text-error">
                    {{ usersStore.error }}
                  </div>
                </div>

                <div class="flex flex-col gap-1 shrink-0">
                  <label class="text-sm font-semibold opacity-70">Antal</label>
                  <div class="bg-base-200 rounded-field flex items-center gap-2 px-3 py-2">
                    <button
                      type="button"
                      class="btn btn-primary btn-circle btn-sm"
                      :disabled="points <= MIN_POINTS"
                      @click="dec"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="size-3.5"
                        viewBox="0 0 448 512"
                        fill="currentColor"
                      >
                        <path
                          d="M432 256c0 17.7-14.3 32-32 32L48 288c-17.7 0-32-14.3-32-32s14.3-32 32-32l352 0c17.7 0 32 14.3 32 32z"
                        />
                      </svg>
                    </button>
                    <span class="text-2xl font-bold tabular-nums w-8 text-center">{{
                      points
                    }}</span>
                    <button
                      type="button"
                      class="btn btn-primary btn-circle btn-sm"
                      :disabled="points >= MAX_POINTS"
                      @click="inc"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="size-3.5"
                        viewBox="0 0 448 512"
                        fill="currentColor"
                      >
                        <path
                          d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 144L48 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l144 0 0 144c0 17.7 14.3 32 32 32s32-14.3 32-32l0-144 144 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-144 0 0-144z"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Reason -->
              <div class="flex flex-col gap-1">
                <label class="text-sm font-semibold opacity-70">Anledning</label>
                <div class="relative">
                  <textarea
                    v-model="reason"
                    class="textarea textarea-lg h-24 w-full pb-6"
                    placeholder="Valfritt"
                    :disabled="submitting"
                  />
                  <span
                    class="absolute bottom-2 right-3 text-xs pointer-events-none"
                    :class="reason.length > MAX_REASON ? 'text-error' : 'text-base-content/40'"
                    >{{ reason.length }}/{{ MAX_REASON }}</span
                  >
                </div>
              </div>

              <div v-if="submitError && mode === 'give'" class="text-sm text-center text-error">
                {{ submitError }}
              </div>

              <button
                type="submit"
                class="btn btn-lg btn-primary w-full"
                :disabled="!canSubmit || submitting"
              >
                <span v-if="submitting" class="loading loading-spinner"></span>
                <span v-else>Ge straff</span>
              </button>
            </form>
          </div>
        </div>

        <!-- Tab: Stryk straff -->
        <input
          type="radio"
          name="create-tabs"
          class="tab"
          aria-label="Stryk straff"
          :checked="mode === 'take'"
          @change="setMode('take')"
        />
        <div class="tab-content">
          <div class="card bg-base-100 shadow-md mt-4 anim-slide-right">
            <form class="card-body gap-5" @submit.prevent="submit">
              <!-- User dropdown + Amount picker -->
              <div class="flex gap-3 items-end">
                <div class="flex flex-col gap-1 flex-1 min-w-0">
                  <label class="text-sm font-semibold opacity-70">För vem?</label>
                  <details ref="dropdownTakeRef" class="dropdown w-full">
                    <summary
                      class="btn btn-lg w-full justify-start font-normal gap-3 [&::-webkit-details-marker]:hidden"
                    >
                      <template v-if="selectedUser">
                        <div class="avatar">
                          <div class="size-7 rounded-full overflow-hidden">
                            <img :src="selectedUser.avatar_url || fallbackAvatar" alt="" />
                          </div>
                        </div>
                        <span class="truncate">{{ selectedUser.username }}</span>
                      </template>
                      <span v-else class="opacity-50">Välj person...</span>
                    </summary>
                    <ul
                      class="dropdown-content bg-base-100 rounded-box z-50 w-full shadow-lg max-h-64 overflow-y-auto p-1 mt-1 flex flex-col gap-0.5"
                    >
                      <li v-if="usersStore.loading" class="flex items-center gap-2 px-3 py-2">
                        <span class="loading loading-spinner loading-sm"></span>
                        <span class="text-sm opacity-70">Laddar...</span>
                      </li>
                      <li v-for="user in usersStore.users" :key="user.id">
                        <button
                          type="button"
                          class="btn btn-ghost w-full justify-start gap-3 font-normal"
                          :class="{ 'btn-active': selectedUserId === user.id }"
                          @click="selectUser(user.id)"
                        >
                          <div class="avatar">
                            <div class="size-7 rounded-full overflow-hidden">
                              <img :src="user.avatar_url || fallbackAvatar" alt="" loading="lazy" />
                            </div>
                          </div>
                          {{ user.username }}
                        </button>
                      </li>
                    </ul>
                  </details>
                  <div v-if="usersStore.error" class="text-sm text-error">
                    {{ usersStore.error }}
                  </div>
                </div>

                <div class="flex flex-col gap-1 shrink-0">
                  <label class="text-sm font-semibold opacity-70">Antal</label>
                  <div class="bg-base-200 rounded-field flex items-center gap-2 px-3 py-2">
                    <button
                      type="button"
                      class="btn btn-primary btn-circle btn-sm"
                      :disabled="points <= MIN_POINTS"
                      @click="dec"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="size-3.5"
                        viewBox="0 0 448 512"
                        fill="currentColor"
                      >
                        <path
                          d="M432 256c0 17.7-14.3 32-32 32L48 288c-17.7 0-32-14.3-32-32s14.3-32 32-32l352 0c17.7 0 32 14.3 32 32z"
                        />
                      </svg>
                    </button>
                    <span class="text-2xl font-bold tabular-nums w-8 text-center">{{
                      points
                    }}</span>
                    <button
                      type="button"
                      class="btn btn-primary btn-circle btn-sm"
                      :disabled="points >= MAX_POINTS"
                      @click="inc"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="size-3.5"
                        viewBox="0 0 448 512"
                        fill="currentColor"
                      >
                        <path
                          d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 144L48 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l144 0 0 144c0 17.7 14.3 32 32 32s32-14.3 32-32l0-144 144 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-144 0 0-144z"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Filler: same height as reason textarea to keep card size stable -->
            <div class="flex flex-col gap-1">
              <label class="text-sm font-semibold opacity-70 invisible">_</label>
              <div class="flex items-center justify-around h-24">
                <ProfilePicture
                  :avatarUrl="authStore.user?.avatar_url || fallbackAvatar"
                  sizeClass="size-14"
                  ringColorClass="ring-primary"
                />
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" class="size-10 fill-base-content/40">
                  <path d="M155.6 17.3C163 3 179.9-3.6 195 1.9l125 45.6 125-45.6c15.1-5.5 32 1.1 39.4 15.4l78.8 152.9c28.8 55.8 10.3 122.3-38.5 156.6l31.3 86.2 41-15c16.6-6 35 2.5 41 19.1s-2.5 35-19.1 41c-47.4 17.3-94.8 34.5-142.2 51.8-16.6 6.1-35-2.5-41-19.1s2.5-35 19.1-41l41-15-31.3-86.2c-59.4 5.2-116.2-33.9-130-95.2l-14.6-64.7-14.6 64.7c-13.8 61.3-70.6 100.4-130 95.2l-31.3 86.2 41 15c16.6 6.1 25.2 24.4 19.1 41s-24.4 25.2-41 19.1c-47.4-17.3-94.8-34.6-142.2-51.8-16.6-6.1-25.2-24.4-19.1-41S26.3 392 42.9 398l41 15 31.3-86.2C66.5 292.5 48.1 226 76.9 170.2L155.6 17.3zm44 54.4l-27.2 52.8 89.2 32.5 13.1-57.9-75.1-27.4zm240.9 0l-75.1 27.4 13.1 57.9 89.2-32.5-27.2-52.8z"/>
                </svg>
                <ProfilePicture
                  v-if="selectedUser"
                  :avatarUrl="selectedUser.avatar_url || fallbackAvatar"
                  sizeClass="size-14"
                  ringColorClass="ring-primary"
                />
                <div v-else class="avatar">
                  <div class="size-14 ring-2 ring-offset-2 ring-primary ring-offset-base-100 rounded-full overflow-hidden bg-base-200 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512" class="size-7 fill-base-content/40">
                      <path d="M64 160c0-53 43-96 96-96s96 43 96 96c0 42.7-27.9 78.9-66.5 91.4-28.4 9.2-61.5 35.3-61.5 76.6l0 24c0 17.7 14.3 32 32 32s32-14.3 32-32l0-24c0-1.7 .6-4.1 3.5-7.3 3-3.3 7.9-6.5 13.7-8.4 64.3-20.7 110.8-81 110.8-152.3 0-88.4-71.6-160-160-160S0 71.6 0 160c0 17.7 14.3 32 32 32s32-14.3 32-32zm96 352c22.1 0 40-17.9 40-40s-17.9-40-40-40-40 17.9-40 40 17.9 40 40 40z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="submitError && mode === 'take'" class="text-sm text-center text-error">
                {{ submitError }}
              </div>

              <button
                type="submit"
                class="btn btn-lg btn-primary w-full"
                :disabled="!canSubmit || submitting"
              >
                <span v-if="submitting" class="loading loading-spinner"></span>
                <span v-else>Stryk straff</span>
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- Non-vest users: plain give form -->
      <div v-else class="card bg-base-100 shadow-md anim-slide-right">
        <form class="card-body gap-5" @submit.prevent="submit">
          <div class="flex gap-3 items-end">
            <div class="flex flex-col gap-1 flex-1 min-w-0">
              <label class="text-sm font-semibold opacity-70">Till vem?</label>
              <details ref="dropdownRef" class="dropdown w-full">
                <summary
                  class="btn btn-lg w-full justify-start font-normal gap-3 [&::-webkit-details-marker]:hidden"
                >
                  <template v-if="selectedUser">
                    <div class="avatar">
                      <div class="size-7 rounded-full overflow-hidden">
                        <img :src="selectedUser.avatar_url || fallbackAvatar" alt="" />
                      </div>
                    </div>
                    <span class="truncate">{{ selectedUser.username }}</span>
                  </template>
                  <span v-else class="opacity-50">Välj person...</span>
                </summary>
                <ul
                  class="dropdown-content bg-base-100 rounded-box z-50 w-full shadow-lg max-h-64 overflow-y-auto p-1 mt-1 flex flex-col gap-0.5"
                >
                  <li v-if="usersStore.loading" class="flex items-center gap-2 px-3 py-2">
                    <span class="loading loading-spinner loading-sm"></span>
                    <span class="text-sm opacity-70">Laddar...</span>
                  </li>
                  <li v-for="user in usersStore.users" :key="user.id">
                    <button
                      type="button"
                      class="btn btn-ghost w-full justify-start gap-3 font-normal"
                      :class="{ 'btn-active': selectedUserId === user.id }"
                      @click="selectUser(user.id)"
                    >
                      <div class="avatar">
                        <div class="size-7 rounded-full overflow-hidden">
                          <img :src="user.avatar_url || fallbackAvatar" alt="" loading="lazy" />
                        </div>
                      </div>
                      {{ user.username }}
                    </button>
                  </li>
                </ul>
              </details>
              <div v-if="usersStore.error" class="text-sm text-error">{{ usersStore.error }}</div>
            </div>

            <div class="flex flex-col gap-1 shrink-0">
              <label class="text-sm font-semibold opacity-70">Antal</label>
              <div class="bg-base-200 rounded-field flex items-center gap-2 px-3 py-2">
                <button
                  type="button"
                  class="btn btn-primary btn-circle btn-sm"
                  :disabled="points <= MIN_POINTS"
                  @click="dec"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="size-3.5"
                    viewBox="0 0 448 512"
                    fill="currentColor"
                  >
                    <path
                      d="M432 256c0 17.7-14.3 32-32 32L48 288c-17.7 0-32-14.3-32-32s14.3-32 32-32l352 0c17.7 0 32 14.3 32 32z"
                    />
                  </svg>
                </button>
                <span class="text-2xl font-bold tabular-nums w-8 text-center">{{ points }}</span>
                <button
                  type="button"
                  class="btn btn-primary btn-circle btn-sm"
                  :disabled="points >= MAX_POINTS"
                  @click="inc"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="size-3.5"
                    viewBox="0 0 448 512"
                    fill="currentColor"
                  >
                    <path
                      d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 144L48 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l144 0 0 144c0 17.7 14.3 32 32 32s32-14.3 32-32l0-144 144 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-144 0 0-144z"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <label class="text-sm font-semibold opacity-70">Anledning</label>
            <div class="relative">
              <textarea
                v-model="reason"
                class="textarea textarea-lg h-24 w-full pb-6"
                placeholder="Valfritt"
                :disabled="submitting"
              />
              <span
                class="absolute bottom-2 right-3 text-xs pointer-events-none"
                :class="reason.length > MAX_REASON ? 'text-error' : 'text-base-content/40'"
                >{{ reason.length }}/{{ MAX_REASON }}</span
              >
            </div>
          </div>

          <div v-if="submitError" class="text-sm text-center text-error">{{ submitError }}</div>

          <button
            type="submit"
            class="btn btn-lg btn-primary w-full"
            :disabled="!canSubmit || submitting || !canGive"
          >
            <span v-if="submitting" class="loading loading-spinner"></span>
            <span v-else>Ge straff</span>
          </button>
        </form>
      </div>
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
