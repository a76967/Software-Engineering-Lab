<template>
    <v-dialog v-model="internalDialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">{{ title }}</v-card-title>
        <v-card-text>
          {{ message }}
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text color="primary" @click="closeDialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  export default Vue.extend({
    name: 'InfoDialog',
    props: {
      value: { type: Boolean, default: false },
      title: { type: String, default: 'Warning' },
      message: { type: String, default: '' }
    },
    computed: {
      internalDialog: {
        get() { return this.value },
        set(val: boolean) { this.$emit('input', val) }
      }
    },
    methods: {
      closeDialog() { this.$emit('input', false) }
    }
  })
  </script>
  
  <style scoped>
  </style>