import { defineStore } from "pinia";
import {
  apiCreatePunishmentEvent,
  apiListPendingPunishmentEvents,
  apiListConfirmedPunishmentEvents,
  apiConfirmPunishmentEvent,
  apiDeletePunishmentEvent,
  apiTakePunishmentEvent,
  type PunishmentEvent,
} from "@/lib/punishmentsApi";

type State = {
  ready: boolean;
  loadingPending: boolean;
  loadingConfirmed: boolean;
  error: string | null;

  pending: PunishmentEvent[];
  confirmed: PunishmentEvent[];

  creating: boolean;
  createError: string | null;

  confirming: boolean;
  confirmError: string | null;
};

type FetchOpts = { target_id?: number; limit?: number };

export const usePunishmentsStore = defineStore("punishments", {
  state: (): State => ({
    ready: false,
    loadingPending: false,
    loadingConfirmed: false,
    error: null,

    pending: [],
    confirmed: [],

    creating: false,
    createError: null,

    confirming: false,
    confirmError: null,
  }),

  actions: {
    async fetchPending(opts?: FetchOpts) {
      this.loadingPending = true;
      this.error = null;
      try {
        this.pending = await apiListPendingPunishmentEvents(opts);
      } catch (e) {
        this.pending = [];
        this.error = e instanceof Error ? e.message : "Failed to load pending punishments";
      } finally {
        this.loadingPending = false;
        this.ready = true;
      }
    },

    async fetchConfirmed(opts?: FetchOpts) {
      this.loadingConfirmed = true;
      this.error = null;
      try {
        this.confirmed = await apiListConfirmedPunishmentEvents(opts);
      } catch (e) {
        this.confirmed = [];
        this.error = e instanceof Error ? e.message : "Failed to load confirmed punishments";
      } finally {
        this.loadingConfirmed = false;
        this.ready = true;
      }
    },

    async fetchAll(opts?: FetchOpts & { confirmedLimit?: number }) {
      // If you want different limits for each list:
      const pendingOpts: FetchOpts = { target_id: opts?.target_id, limit: opts?.limit };
      const confirmedOpts: FetchOpts = {
        target_id: opts?.target_id,
        limit: opts?.confirmedLimit ?? opts?.limit,
      };

      await Promise.all([this.fetchPending(pendingOpts), this.fetchConfirmed(confirmedOpts)]);
    },

    async createEvent(input: { target_id: number; amount: number; reason?: string }) {
      this.creating = true;
      this.createError = null;

      try {
        const created = await apiCreatePunishmentEvent({
          target_id: input.target_id,
          amount: input.amount,
          reason: (input.reason ?? "").trim() || "",
        });

        // created is pending
        this.pending.unshift(created);
        return created;
      } catch (e) {
        this.createError = e instanceof Error ? e.message : "Failed to create punishment";
        throw e;
      } finally {
        this.creating = false;
      }
    },

    async confirmEvent(eventId: number) {
      this.confirming = true;
      this.confirmError = null;

      try {
        const updated = await apiConfirmPunishmentEvent(eventId);

        // remove from pending
        this.pending = this.pending.filter((e) => e.id !== eventId);

        // add to confirmed (most recent first)
        this.confirmed.unshift(updated);

        return updated;
      } catch (e) {
        this.confirmError = e instanceof Error ? e.message : "Failed to confirm punishment";
        throw e;
      } finally {
        this.confirming = false;
      }
    },

    async deleteEvent(eventId: number) {
      try {
        await apiDeletePunishmentEvent(eventId);
        this.pending = this.pending.filter((e) => e.id !== eventId);
      } catch (e) {
        this.error = e instanceof Error ? e.message : "Failed to delete punishment";
        throw e;
      }
    },

    async takeEvent(input: { target_id: number; amount: number }) {
      const created = await apiTakePunishmentEvent(input);
      return created;
    },
  },
});
