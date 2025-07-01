<template>
    <v-card>
      <v-card-title>Set Perspective Items</v-card-title>
      <v-card-text>
        <v-alert v-if="errorMessage" type="error" dense class="mb-4">
          {{ errorMessage }}
        </v-alert>
        <div v-if="items.length" class="mb-4">
          <div v-for="it in items" :key="it.id">
            <strong>{{ it.name }}</strong> - {{ it.data_type }}
            <span v-if="it.required">(required)</span>
          </div>
        </div>
        <v-form ref="form" v-model="isValid" lazy-validation>
          <v-text-field
            v-model="newItem.name"
            label="Name"
            required
            :rules="nameRules"
          />
          <v-select
            v-model="newItem.data_type"
            :items="types"
            label="Data Type"
            required
            :rules="dataTypeRules"
          />
          <v-checkbox v-model="newItem.required" label="Required" />
          <v-btn
            color="primary"
            class="mt-3"
            :disabled="!isValid"
            @click="addItem"
          >
            Add
          </v-btn>
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
        isValid: false,
        errorMessage: '',
        nameRules: [
          (v: string) => !!v || 'Name is required',
          (v: string) =>
            !this.items.some(it => it.name === v) ||
            'Name already exists'
        ],
        dataTypeRules: [
          (v: string) => !!v || 'Data Type is required',
          (v: string) =>
            this.types.includes(v) ||
            'Invalid Data Type'
        ]
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
        if (!(this.$refs.form as any).validate()) return
        this.errorMessage = ''
        try {
          await axios.post(`/v1/projects/${this.projectId}/perspective-items/`, this.newItem)
          this.newItem = { name: '', data_type: '', required: false }
          this.fetchItems()
        } catch (err: any) {
          const data = err.response?.data || {}
          this.errorMessage =
            data.name?.[0] ||
            data.data_type?.[0] ||
            data.required?.[0] ||
            data.non_field_errors?.join(', ') ||
            'Please fill all required fields and avoid duplicate names.'
        }
      }
    }
  })
  </script>