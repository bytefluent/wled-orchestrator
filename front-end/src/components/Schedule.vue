<template>
  <v-card class="ma-2 pa-2" color="#24354633">
    <div class="d-flex flex justify-space-between">
      <div><div class="f-28 d-inline-block mr-4">{{schedule.name}}</div> <div class="d-inline-block mr-4">{{start_time}} <v-icon>mdi-arrow-right-bold</v-icon> {{end_time}}</div>
      <v-chip v-for="(g, i) in schedule.string_json" :key="i">{{group_by_id[g].name}}</v-chip>
      </div>
      <div>
      <v-switch
          class="ma-2 d-inline-block"
          :input-value="schedule.enabled"
          inset
          small
          color="success"
          @change="() => toggle()"
        ></v-switch>
        <v-btn @click="schedule_dialog = true">EDIT</v-btn>
      </div>
    </div>

    <v-dialog
      v-model="schedule_dialog"
      max-width="600px"
    >
      <v-card>
        <v-card-title>
          <span class="text-h5">LED Schedule</span>
        </v-card-title>
        <v-card-text>
          <div class="d-flex flex">
            <v-text-field
              v-model="schedule.name"
              label="Schedule Name"
              outlined
            ></v-text-field>
            <v-autocomplete
              v-model="schedule.string_json"
              :items="Object.values(groups)"
              label="Groups"
              outlined
              chips
              multiple
              item-text="name"
              item-value="id"
            ></v-autocomplete>
          </div>
          <div class="d-flex flex">
            <v-menu
              v-model="start_time_picker"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-text-field
                  v-model="start_time"
                  label="Start Time"
                  prepend-icon="mdi-clock-time-four-outline"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="start_time_picker"
                v-model="start_time"
                format="ampm"
                full-width
              ></v-time-picker>
            </v-menu>
            <v-menu
              v-model="end_time_picker"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-text-field
                  v-model="end_time"
                  label="End Time"
                  prepend-icon="mdi-clock-time-four-outline"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                  :hint="next_day() ? 'Next Day' : ''"
                  persistent-hint
                >
                </v-text-field>
              </template>
              <v-time-picker
                v-if="end_time_picker"
                v-model="end_time"
                format="ampm"
                full-width
              ></v-time-picker>
            </v-menu>
          </div>
          <h4>Intervals</h4>
          <div v-for="(interval, i) in schedule.effects_json" :key=i>
            <PatternInterval :interval="interval" :index="i" @remove="remove_interval" />
          </div>
          <v-btn small @click="add_interval">Add Interval</v-btn>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="red darken-1"
            text
            @click="schedule_dialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="blue darken-1"
            text
            @click="save_schedule"
          >
            Save
          </v-btn>
          <v-btn
            v-if="schedule.id"
            color="green darken-1"
            text
            @click="save_schedule_new"
          >
            Save New
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import {mapState} from "vuex"
import PatternInterval from "@/components/PatternInterval.vue";

export default {
  name: "Schedule",
  props: {
    schedule: Object,
  },
  components: {
    PatternInterval
  },
  data: () => ({
    schedule_dialog: false,
    start_time: "00:00",
    end_time: "00:00",
    start_time_picker: false,
    end_time_picker: false,
  }),
  computed: {
    ...mapState(["groups", "group_by_id"])
  },
  sockets: {
  },
  methods: {
    save_schedule: function() {
      this.schedule.start_time = this.hm_to_seconds(this.start_time);
      this.schedule.end_time = this.hm_to_seconds(this.end_time);
      this.$socket.emit('command', {command: 'save_schedule', schedule: this.schedule});
      this.schedule_dialog = false;
    },
    save_schedule_new: function() {
      this.schedule.id = null;
      this.schedule.start_time = this.hm_to_seconds(this.start_time);
      this.schedule.end_time = this.hm_to_seconds(this.end_time);
      this.$socket.emit('command', {command: 'save_schedule', schedule: this.schedule});
      this.schedule_dialog = false;
    },
    seconds_to_hm: function(seconds) {
      var h = Math.floor(seconds % (3600*24) / 3600);
      var m = Math.floor(seconds % 3600 / 60);
      // var s = Math.floor(seconds % 60);

      var sHours   = new String(h).padStart(2, '0');
      var sMinutes = new String(m).padStart(2, '0');

      return `${sHours}:${sMinutes}`
    },
    hm_to_seconds: function(hm) {
      let parts = hm.split(":");
      return (parseInt(parts[0]) * 3600) + (parseInt(parts[1]) * 60)
    },
    add_interval: function() {
      this.schedule.effects_json.push({pattern: null, duration: 180});
    },
    remove_interval: function(i) {
      this.schedule.effects_json.splice(i, 1)
    },
    next_day: function() {
      return this.hm_to_seconds(this.end_time) < this.hm_to_seconds(this.start_time)
    },
    toggle: function() {
      this.schedule.enabled = !this.schedule.enabled;
      this.save_schedule()
    }
  },
  mounted() {
    this.$nextTick(function () {
      this.start_time = this.seconds_to_hm(this.schedule.start_time)
      this.end_time = this.seconds_to_hm(this.schedule.end_time)

      if(!this.schedule.id) {
        this.schedule_dialog = true;
      }
    })
  }
};
</script>
