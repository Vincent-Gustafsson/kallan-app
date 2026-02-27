import { defineStore } from "pinia";
import { apiUsers, apiUser, type UserMini } from "@/lib/usersApi.ts";

type State = {
  ready: boolean;
  loading: boolean;
  error: string | null;

  q: string;
  excludeMe: boolean;
  limit: number;

  users: UserMini[];

  selected: UserMini | null;
  loadingSelected: boolean;
  selectedError: string | null;
};

export const useUsersStore = defineStore("users", {
  state: (): State => ({
    ready: false,
    loading: false,
    error: null,

    q: "",
    excludeMe: true,
    limit: 20,

    users: [],

    selected: null,
    loadingSelected: false,
    selectedError: null,
  }),

  actions: {
    async fetch(params?: { q?: string; excludeMe?: boolean; limit?: number }) {
      this.loading = true;
      this.error = null;

      const q = params?.q ?? this.q;
      const excludeMe = params?.excludeMe ?? this.excludeMe;
      const limit = params?.limit ?? this.limit;

      this.q = q;
      this.excludeMe = excludeMe;
      this.limit = limit;

      try {
        this.users = await apiUsers({ q, excludeMe, limit });
      } catch (e) {
        this.users = [];
        this.error = e instanceof Error ? e.message : "Failed to load users";
      } finally {
        this.loading = false;
        this.ready = true;
      }
    },

    clear() {
      this.users = [];
      this.error = null;
      this.ready = true;
    },

    async fetchOne(userId: number) {
      this.loadingSelected = true;
      this.selectedError = null;

      try {
        this.selected = await apiUser(userId);
      } catch (e) {
        this.selected = null;
        this.selectedError = e instanceof Error ? e.message : "Failed to load user";
      } finally {
        this.loadingSelected = false;
        this.ready = true;
      }
    },

    clearSelected() {
      this.selected = null;
      this.selectedError = null;
    },
  },
});
