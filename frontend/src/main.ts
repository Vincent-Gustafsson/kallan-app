import "./assets/base.css";

import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

// Listen ASAP
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.addEventListener("message", (event) => {
    const msg = event.data;
    if (msg?.type === "NAVIGATE" && typeof msg.to === "string") {
      // avoid "NavigationDuplicated"-style noise
      if (router.currentRoute.value.fullPath !== msg.to) {
        router.push(msg.to);
      }
    }
  });

  // Check for SW updates whenever the app becomes visible (e.g. switching back to installed PWA)
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      navigator.serviceWorker.getRegistration().then((reg) => reg?.update());
    }
  });
}

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");
