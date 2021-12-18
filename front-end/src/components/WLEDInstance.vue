<template>
<v-card class="wled-instance ma-2 pa-2" color="#24354633">
  <div class="flex d-flex justify-space-between">
  <a class="f-24 grey--text" :href="'http://'+instance.addr" target="_blank">{{instance.data.info.name}}</a>
    <v-switch
        class="mt-0"
        :input-value="instance.data.state.on"
        inset
        small
        color="success"
        :loading="on ? 'warning' : false"
        @change="toggle"
      ></v-switch>
  </div>
  
  
  <div class="flex d-flex justify-space-between">
       <v-select
          class="ma-2"
          :items="patterns"
          :value="current_pattern()"
          item-text="name"
          item-value="id"
          label="Pattern"
          outlined
          @change="select_pattern"
        ></v-select>
        <v-btn
          class="mt-4 mr-2"
          color="primary"
          dark
          large
          @click="show_pattern_dialog"
        >
          <v-icon>mdi-lightbulb-group-outline</v-icon>
        </v-btn>
  </div>

 <v-dialog
      v-model="pattern_dialog"
      max-width="600px"
    >
      <v-card>
        <v-card-title>
          <span class="text-h5">LED Pattern</span>
        </v-card-title>
        <v-card-text>
          <v-text-field
            v-model="pattern_name"
            label="Pattern Name"
            outlined
          ></v-text-field>
      <div class="flex d-flex justify-space-between">
       <v-select
          class="ma-2"
          :items="effects"
          :value="current_effect"
          label="Effects"
          outlined
          @change="select_effect"
        ></v-select>
       <v-select
          class="ma-2"
          :items="palettes"
          :value="current_palette"
          label="Palettes"
          outlined
          @change="select_palette"
        ></v-select>
      </div>
      <div>
        <div class="flex d-flex justify-space-around">
          <color-picker :value="current_color()" @color:change="set_color"/>
        </div>
        <div class="flex d-flex justify-center">
          <v-btn
            class="ma-2"
            :class="[activeColor == 0 ? 'active' : '']"
            :style="{backgroundColor:color1.hex()}"
            fab
            x-large
            dark
            @click="activeColor = 0"
          >
            1
          </v-btn>
          <v-btn
            class="ma-2"
            :class="[activeColor == 1 ? 'active' : '']"
            :style="{backgroundColor:color2.hex()}"
            fab
            x-large
            dark
            @click="activeColor = 1"
          >
            2
          </v-btn>
          <v-btn
            class="ma-2"
            :class="[activeColor == 2 ? 'active' : '']"
            :style="{backgroundColor:color3.hex()}"
            fab
            x-large
            dark
            @click="activeColor = 2"
          >
            3
          </v-btn>
        </div>
          <v-slider
            label="Intensity"
            :value="current_intensity"
            @change="set_intensity"
            class="mt-4"
            min="0"
            max="255"
          ></v-slider>
          <v-slider
            label="Speed"
            color="primary"
            :value="current_speed"
            @change="set_speed"
            min="0"
            max="255"
          ></v-slider>
      </div>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="red darken-1"
            text
            @click="pattern_dialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="blue darken-1"
            text
            @click="save_pattern"
          >
            Save
          </v-btn>
          <v-btn
            color="green darken-1"
            text
            @click="save_pattern_new"
          >
            Save New
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import chroma from 'chroma-js';

import { mapState } from "vuex";

export default {
  name: "WLEDInstance",
  props: {
    instance: Object,
  },
  data: () => ({
    on: false,
    pattern_dialog: false,
    activeColor: 0,
    pattern_name: null,
  }),
  sockets: {
  },
  methods: {
    refresh: function() {
      this.$socket.emit('refresh');
    },
    toggle: function(v) {
      this.$socket.emit('command', {server: this.instance.server, command: 'power', on: v});
    },
    save_pattern: function() {
      this.pattern_dialog = false;
      this.$socket.emit('command', {
        server: this.instance.server, 
        command: 'save_pattern', 
        name: this.pattern_name, 
        id: this.instance.pattern});
    },
    save_pattern_new: function() {
      this.pattern_dialog = false;
      this.$socket.emit('command', {server: this.instance.server, command: 'save_pattern', name: this.pattern_name});
    },
    select_pattern: function(pattern_id) {
      this.$socket.emit('command', {server: this.instance.server, command: 'set_pattern', id: pattern_id});
    },
    set_color: function(d) {
      let color = chroma(d.color.hexString)
      if(d.color.hexString === this.current_color()) {
        return
      }
      this.$socket.emit('update', {
        server: this.instance.server, 
        color1: this.activeColor == 0 ? color.rgb() : null,
        color2: this.activeColor == 1 ? color.rgb() : null,
        color3: this.activeColor == 2 ? color.rgb() : null,
        });
    },
    select_palette: function(p) {
      this.$socket.emit('update', {
        server: this.instance.server, 
        palette: p
        });
    },
    select_effect: function(e) {
      this.$socket.emit('update', {
        server: this.instance.server, 
        effect: e
        });
    },
    set_intensity: function(i) {
      this.$socket.emit('update', {
        server: this.instance.server, 
        intensity: i
        });
    },
    set_speed: function(s) {
      this.$socket.emit('update', {
        server: this.instance.server, 
        speed: s
        });
    },
    current_color: function() {
      return chroma(this.instance.data.state.seg[0].col[this.activeColor]).hex();
    },
    is_on: function() {
      return this.instance.data.state.seg[0].on;
    },
    show_pattern_dialog: function() {
      this.pattern_name = this.patterns_by_id[this.instance.pattern].name;
      this.pattern_dialog = true;
    },
    current_pattern: function() {
      return this.patterns_by_id[this.instance.pattern];
    }
  },
  computed: {
    ...mapState(["patterns", "patterns_by_id", "effects", "palettes"]),
    color1: function() {
      return chroma(this.instance.data.state.seg[0].col[0].slice(0, 3));
    },
    color2: function() {
      return chroma(this.instance.data.state.seg[0].col[1].slice(0, 3));
    },
    color3: function() {
      return chroma(this.instance.data.state.seg[0].col[2].slice(0, 3));
    },
    current_palette() {
      return this.palettes[this.instance.data.state.seg[0].pal];
    },
    current_effect() {
      return this.effects[this.instance.data.state.seg[0].fx];
    },
    current_speed() {
      return this.instance.data.state.seg[0].sx;
    },
    current_intensity() {
      return this.instance.data.state.seg[0].ix;
    },
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.active {
  border: solid white 2px;
}

.wled-instance {
  width: 360px;
}
</style>
