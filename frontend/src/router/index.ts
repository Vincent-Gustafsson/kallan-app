import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { usePunishmentsStore } from "@/stores/punishments";
import { useUsersStore } from "@/stores/users";

import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue";
import SetPasswordView from "@/views/SetPasswordView.vue";
import PunishmentsView from "@/views/PunishmentsView.vue";
import PeopleView from "@/views/PeopleView.vue";
import ProfileView from "@/views/ProfileView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView, meta: { hideBottomBar: true } },
    {
      path: "/set-password",
      name: "set-password",
      component: SetPasswordView,
      meta: { hideBottomBar: true },
    },

    {
      path: "/",
      name: "home",
      component: HomeView,
      beforeEnter: async () => {
        const usersStore = useUsersStore();
        if (!usersStore.loading) usersStore.fetch({ q: "", excludeMe: true });
      },
    },
    {
      path: "/punishments",
      name: "punishments",
      component: PunishmentsView,
      beforeEnter: async () => {
        const punishStore = usePunishmentsStore();
        const usersStore = useUsersStore();
        if (!usersStore.loading) usersStore.fetch({ q: "", excludeMe: true });
        if (!punishStore.loadingPending) punishStore.fetchPending();
        if (!punishStore.loadingConfirmed) punishStore.fetchConfirmed({ limit: 10 });
      },
    },
    {
      path: "/users",
      name: "users",
      component: PeopleView,
      beforeEnter: async () => {
        const usersStore = useUsersStore();
        if (!usersStore.loading) usersStore.fetch({ q: "", excludeMe: true });
      },
    },
    { path: "/users/:id", name: "user", component: ProfileView },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (!auth.ready) {
    await auth.refresh();
  }

  const isLogin = to.name === "login";
  const isSetPassword = to.name === "set-password";

  // 1) Not logged in -> only allow login route
  if (!auth.isAuthed && !isLogin) {
    return { name: "login" };
  }

  // 2) Logged in but forced reset -> only allow set-password route
  if (auth.isAuthed && auth.mustResetPassword && !isSetPassword) {
    return { name: "set-password" };
  }

  // 3) Logged in and NOT forced reset -> keep them out of login/set-password
  if (auth.isAuthed && !auth.mustResetPassword && (isLogin || isSetPassword)) {
    return { name: "home" };
  }

  return true;
});

export default router;
