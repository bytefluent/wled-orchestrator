import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import "./plugins/color-picker";
import VueSocketIO from "vue-socket.io";

import "@fontsource/roboto";
import "@mdi/font/css/materialdesignicons.css"
import "./styles/main.scss"

const is_development = process.env.NODE_ENV === 'development'

Vue.use(
  new VueSocketIO({
    debug: is_development,
    connection: is_development ? "http://localhost:8889" : window.location.origin,
    vuex: {
      store,
      actionPrefix: "SOCKET_",
      mutationPrefix: "SOCKET_"
    }
  })
);

Vue.config.productionTip = true;

new Vue({
  router,
  store,
  vuetify,
  render: (h) => h(App),
}).$mount("#app");


