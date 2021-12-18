import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

function isObject(objValue) {
  return objValue && typeof objValue === 'object' && objValue.constructor === Object;
}
function isArray(arrValue) {
  return Object.prototype.toString.call(arrValue) === '[object Array]';
}

function isSimple(value) {
  return !(isObject(value) || isArray(value))
}

function update_recursive(existing, fresh) {
  if(isObject(fresh)) {
    Object.keys(fresh).forEach(k => {
      let v = existing[k];
      if(isSimple(v)) {
        Vue.set(existing, k, fresh[k]);
      } else {
        update_recursive(v, fresh[k]);
      }
    })
  } else if(isArray(fresh)) {
    for(let i = 0; i < fresh.length; i++) {
      if(isSimple(existing[i])) {
        Vue.set(existing, i, fresh[i]);
      } else {
        update_recursive(existing[i], fresh[i]);
      }
    }
  }
}

export default new Vuex.Store({
  state: {
    patterns: [],
    patterns_by_id: {},
    schedules: [],
    groups: [],
    group_by_id: {},
    effects: [],
    palettes: [],
    settings: {},
    leds: {}
  },
  mutations: {
    set_patterns: function(state, data) {
      state.patterns = data;
      data.forEach(p => {
        Vue.set(state.patterns_by_id, p.id, p);
      })
    },
    set_schedules: function(state, data) {
      state.schedules = data;
    },
    set_groups: function(state, data) {
      state.groups = data;
      data.forEach(p => {
        Vue.set(state.group_by_id, p.id, p);
      })
    },
    set_effects: function(state, data) {
      state.effects = data;
    },
    set_palettes: function(state, data) {
      state.palettes = data;
    },
    set_leds: function(state, leds) {
      Object.keys(leds).forEach(l => {
        let m = leds[l]
        if(m.server in state.leds) {
          update_recursive(state.leds[m.server], m);
        } else {
          Vue.set(state.leds, m.server, m);
        }
      })
    },
    set_settings: function(state, data) {
      Object.keys(data).forEach(k => {
        Vue.set(state.settings, k, data[k]);
      })
    },
    new_group: function(state) {
      state.groups.push({
        name: '- new group -',
        group_json: []
      })
    },
    new_schedule: function(state) {
      state.schedules.push({
        name: '- new schedule -',
        start_time: 0, 
        end_time: 0,
        string_json: [],
        effects_json: []
      })
    }
  },
  actions: {},
  modules: {},
});
