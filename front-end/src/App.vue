<template>
  <v-app id="app">
    <div id="nav" class="d-flex">
      <img src="wled_logo_akemi.png" style="height:52px" @click="refresh"/> <div @click="refresh" class="d-inline-block mx-3 f-32 text--primary">Orchestrator</div>
      <v-spacer class="d-inline-block" />
      <v-switch
          class="ma-2"
          :input-value="settings.schedule_on"
          inset
          small
          label="Automatic"
          color="success"
          @change="() => toggle('schedule_on')"
        ></v-switch>
    </div>
    <router-view />
    {{settings}}
  </v-app>
</template>

<script>
import { mapState } from "vuex";
// import view_common from "@/mixins/view-common";

export default {
  name: "App",
  // mixins: [view_common],
  components: {},

  computed: {
    ...mapState(["settings"])
  },
  methods: {
    refresh: function() {
      this.$socket.emit('refresh');
    },
    toggle: function(setting) {
      this.$socket.emit('command', {command: 'set_setting', key: setting, value: !this.settings[setting]});
    }
  },
  sockets: {
    data: () => ({
      error: null
    })
  }
};
</script>

<style lang="scss">
#app {
  font-family: Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

#nav {

  a {
    line-height: 50px;
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}

</style>
