<template>
  <v-card class="ma-2 pa-2">
    <div class="d-flex flex">
      <v-select
        class="mx-2"
        :items="patterns"
        :value="current_pattern()"
        item-text="name"
        item-value="id"
        label="Pattern"
        outlined
        @change="select_pattern"
      ></v-select>
      <v-text-field
        v-model="interval.duration"
        label="Interval (seconds)"
        type="integer"
        outlined
      ></v-text-field>
      <v-btn icon color="red" @click="() => $emit('remove', index)"><v-icon>mdi-close-box</v-icon></v-btn>
    </div>
  </v-card>
</template>

<script>
import {mapState} from "vuex"

export default {
  name: "PatternInterval",
  props: {
    interval: Object,
    index: Number
  },
  components: {
  },
  data: () => ({
  }),
  computed: {
    ...mapState(["patterns", "patterns_by_id"])
  },
  sockets: {
  },
  methods: {
    select_pattern: function(pattern_id) {
      this.interval.pattern = pattern_id;
    },
    current_pattern: function() {
      return this.patterns_by_id[this.interval.pattern];
    }
  }
};
</script>
