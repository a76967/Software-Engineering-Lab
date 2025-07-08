<template>
    <v-card>
      <v-alert v-if="errorMessage" type="error" dense>
        {{ errorMessage }}
      </v-alert>
      <v-card-text>
        <v-form ref="form" v-model="isValid" lazy-validation>
          <v-text-field v-model="item.name" label="Name" required :rules="nameRules" />
          <v-select
            v-model="item.admin_perspective"
            :items="adminPerspectives"
            item-text="name"
            item-value="id"
            label="Admin Perspective"
            required
          />
          <v-select
            v-model="item.data_type"
            :items="types"
            label="Data Type"
            required
            :rules="dataTypeRules"
            disabled
          />
          <v-text-field
            v-if="item.data_type === 'enum'"
            v-model="enumValues"
            label="Enum Values (comma-separated)"
          />
          <v-checkbox v-model="item.required" label="Required" />
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-end">
        <v-btn text @click="cancel">{{ $t('generic.cancel') }}</v-btn>
        <v-btn color="primary" :disabled="!isValid || hasPerspectives" class="ms-2" @click="save">
          {{ $t('generic.save') }}
        </v-btn>
      </v-card-actions>
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
        item: { name: '', admin_perspective: null, data_type: '', required: false } as any,
        enumValues: '',
        isValid: false,
        adminPerspectives: [] as any[],
        types: ['string', 'number', 'boolean', 'enum'],
        errorMessage: '',
        hasPerspectives: false,
        nameRules: [(v: string) => !!v || 'Name is required'],
        dataTypeRules: [(v: string) => !!v || 'Data Type is required']
      }
    },
  
    computed: {
      projectId(): number {
        return Number(this.$route.params.id)
      },
      itemId(): number {
        return Number(this.$route.query.itemId)
      }
    },
  
    mounted() {
      this.checkPerspectives()
      this.fetchAdminPerspectives()
      this.fetchItem()
    },
  
    methods: {
      async checkPerspectives() {
        try {
          const res = await axios.get(`/v1/projects/${this.projectId}/perspectives/`, { params: { limit: 1 } })
          const data = res.data.results || res.data
          if (data.length > 0) {
            this.hasPerspectives = true
            this.$router.push({
              path: this.localePath('/message'),
              query: {
                message: 'User perspectives exist. Delete them to modify these items.',
                redirect: this.localePath(`/projects/${this.projectId}/perspective-items`)
              }
            })
          }
        } catch {
          this.hasPerspectives = false
        }
      },
      async fetchAdminPerspectives() {
        try {
          const res = await axios.get(`/v1/projects/${this.projectId}/admin-perspectives/`)
          this.adminPerspectives = res.data.results || res.data
        } catch {
          this.adminPerspectives = []
        }
      },
      async fetchItem() {
        try {
          const { data } = await axios.get(`/v1/projects/${this.projectId}/perspective-items/${this.itemId}/`)
          this.item = { ...data }
          if (this.item.data_type === 'enum') {
            this.enumValues = (data.enum || []).join(', ')
          }
        } catch {
          this.errorMessage = 'Failed to load item.'
        }
      },
      async save() {
        if (this.hasPerspectives) return
        if (!(this.$refs.form as any).validate()) return
        const payload: any = {
          name: this.item.name,
          admin_perspective: this.item.admin_perspective,
          required: this.item.required
        }
        if (this.item.data_type === 'enum') {
          payload.enum = this.enumValues.split(',').map((s: string) => s.trim()).filter((s: string) => s)
        }
        try {
          await axios.patch(`/v1/projects/${this.projectId}/perspective-items/${this.itemId}/`, payload)
          this.$router.push({
            path: this.localePath('/message'),
            query: {
              message: 'Perspective item updated!',
              redirect: this.localePath(`/projects/${this.projectId}/perspective-items`)
            }
          })
        } catch (err: any) {
          const data = err.response?.data || {}
          this.errorMessage =
            data.name?.[0] ||
            data.data_type?.[0] ||
            data.required?.[0] ||
            data.non_field_errors?.join(', ') ||
            'Failed to save. Check required fields or duplicates.'
        }
      },
      cancel() {
        this.$router.push(this.localePath(`/projects/${this.projectId}/perspective-items`))
      }
    }
  })
  </script>
  
  <style scoped>
  .v-card {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
  }
  </style>