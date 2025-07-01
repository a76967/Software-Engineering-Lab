<template>
    <v-card>
      <v-card-title>Set Perspective Items</v-card-title>
      <v-card-text>
        <div v-if="items.length" class="mb-4">
          <div v-for="it in items" :key="it.id">
            <strong>{{ it.name }}</strong> - {{ it.data_type }}
            <span v-if="it.required">(required)</span>
          </div>
        </div>
        <v-form ref="form" v-model="isValid" lazy-validation>
          <v-text-field v-model="newItem.name" label="Name" required />
          <v-select v-model="newItem.data_type" :items="types" label="Data Type" required />
          <v-checkbox v-model="newItem.required" label="Required" />
          <v-btn color="primary" class="mt-3" :disabled="!isValid" @click="addItem">Add</v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import axios from 'axios'
  export default Vue.extend({
    layout: 'project',
    middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],
    data() {
      return {
        items: [] as any[],
        newItem: { name: '', data_type: '', required: false },
        types: ['string', 'number', 'boolean'],
        isValid: false
      }
    },
    computed: {
      projectId(): number {
        return Number(this.$route.params.id)
      }
    },
    mounted() {
      this.fetchItems()
    },
    methods: {
      async fetchItems() {
        try {
          const res = await axios.get(`/v1/projects/${this.projectId}/perspective-items/`)
          this.items = res.data.results || res.data
        } catch (e) {
          this.items = []
        }
      },
      async addItem() {
        await axios.post(`/v1/projects/${this.projectId}/perspective-items/`, this.newItem)
        this.newItem = { name: '', data_type: '', required: false }
        this.fetchItems()
      },
      async addPerspectiveItem(item) {
        const pid = this.$route.params.id
        try {
          await axios.post(
            `/v1/projects/${pid}/perspective-items/`,
            {
              name:      item.text,               
              data_type: item.data_type  || 'string',
              required:  false,
              order:     0
            }
          )
          this.fetchItems()
        } catch (err: any) {
          console.error(
            'Failed to create PerspectiveItem:',
            err.response?.data || err.message
          )
        }
      }
    }
  })
  </script>