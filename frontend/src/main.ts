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
}

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");
