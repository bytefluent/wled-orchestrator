<template>
  <v-card class="ma-2 pa-2" color="#24354633">
    <div class="d-flex flex justify-space-between">
        {{group.name}}
      <v-btn @click="group_dialog = true">EDIT</v-btn>
    </div>
    <v-dialog
      v-model="group_dialog"
      max-width="600px"
    >
      <v-card>
        <v-card-title>
          <span class="text-h5">LED Group</span>
        </v-card-title>
        <v-card-text>
          <div class="d-flex flex">
            <v-text-field
                v-model="group.name"
                label="Group Name"
                outlined
            ></v-text-field>
            <v-autocomplete
                v-model="group.group_json"
                :items="Object.values(leds)"
                chips
                multiple
                item-text="data.info.name"
                item-value="name"
            ></v-autocomplete>
          </div>
          <div class="d-flex flex">
          </div>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="red darken-1"
            text
            @click="group_dialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="blue darken-1"
            text
            @click="save_group"
          >
            Save
          </v-btn>
          <v-btn
            v-if="group.id"
            color="green darken-1"
            text
            @click="save_group_new"
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

export default {
  name: "WLEDGroup",
  props: {
    group: Object,
  },
  components: {
  },
  data: () => ({
      group_dialog: false
  }),
  computed: {
    ...mapState(["leds"])
  },
  sockets: {
  },
  methods: {
    save_group: function() {
      this.$socket.emit('command', {command: 'save_group', group: this.group});
      this.group_dialog = false;
    },
    save_group_new: function() {
      this.group.id = null;
      this.$socket.emit('command', {command: 'save_group', group: this.group});
      this.group_dialog = false;
    }
  }
};
</script>
