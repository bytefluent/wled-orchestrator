<template>
  <div class="home">
    <h3>Strings</h3>
    <div class="flex d-flex flex-wrap">
      <div v-for="(led, s) in leds" :key="s" class="flex d-flex">
        <WLEDInstance :instance="led" />
      </div>
    </div>
    <v-card class="ma-2 pa-2" color="#24354633">
      <div class="ma-2 d-flex flex justify-space-between">
        <h3>Groups</h3>
        <v-btn icon color="secondary" @click="new_group"><v-icon>mdi-plus</v-icon></v-btn>
      </div>
      <div v-for="(group, i) in groups" :key="i">
        <WLEDGroup :group="group" />
      </div>
    </v-card>
    <v-card class="ma-2 pa-2" color="#24354633">
      <div class="ma-2 d-flex flex justify-space-between">
        <h3>Schedules</h3>
        <v-btn icon color="secondary" @click="new_schedule"><v-icon>mdi-plus</v-icon></v-btn>
      </div>
      <div v-for="(schedule, i) in schedules" :key="i">
        <Schedule :schedule="schedule" />
      </div>
    </v-card>
  </div>
</template>

<script>
import {mapState, mapMutations} from "vuex"
// @ is an alias to /src
import WLEDInstance from "@/components/WLEDInstance.vue";
import WLEDGroup from "@/components/WLEDGroup.vue";
import Schedule from "@/components/Schedule.vue";

export default {
  name: "Home",
  components: {
    WLEDInstance,
    WLEDGroup,
    Schedule
  },
  data: () => ({
  }),
  computed: {
    ...mapState(["leds", "groups", "schedules", "settings"])
  },
  sockets: {
    identify: function(session) {
      console.log(session);
      this.$socket.emit('refresh');
    },
    leds: function(leds) {
      this.set_leds(leds)
      this.$forceUpdate();
    },
    state: function(data) {
      console.log(data)
      this.set_patterns(data.patterns);
      this.set_schedules(data.schedules);
      this.set_groups(data.groups);
      this.set_effects(data.effects);
      this.set_palettes(data.palettes);
    },
    settings: function(data) {
      console.log(data)
      this.set_settings(data)
    }
  },
  methods: {
    ...mapMutations([
      "set_patterns", 
      "set_schedules", 
      "set_groups", 
      "set_leds", 
      "set_effects",
      "set_palettes",
      "set_settings",
      "new_group", 
      "new_schedule"]),
  }
};
</script>
