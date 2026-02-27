import { defineStore } from "pinia";
import {
  apiLogin,
  apiMe,
  apiSetPassword,
  apiLogout,
  apiSetAvatar,
  type Me,
} from "@/lib/authApi.ts";

type State = {
  ready: boolean;
  user: Me | null;
};

export const useAuthStore = defineStore("auth", {
  state: (): State => ({
    ready: false,
    user: null,
  }),

  getters: {
    isAuthed: (s) => !!s.user,
    mustResetPassword: (s) => !!s.user?.force_password_reset,
    myTier: (s) => s.user?.tier || "bandana",
    canManageFikapinnar: (s) =>
      (s.user?.permissions ?? []).includes("punishments.manage_fikapinnar"),
  },

  actions: {
    async refresh() {
      try {
        this.user = await apiMe();
      } catch {
        this.user = null;
      } finally {
        this.ready = true;
      }
    },

    async login(username: string, password: string) {
      await apiLogin(username, password);
      this.user = await apiMe();
      this.ready = true;
    },

    setUser(user: Me | null) {
      this.user = user;
      this.ready = true;
    },

    async setPassword(newPassword: string) {
      await apiSetPassword(newPassword);
      this.user = await apiMe(); // refresh so force_password_reset becomes false
    },

    async logout() {
      await apiLogout();
      this.user = null;
      this.ready = true;
    },

    async uploadAvatar(file: File) {
      const me = await apiSetAvatar(file);
      this.user = me;
      this.ready = true;
    },
  },
});
