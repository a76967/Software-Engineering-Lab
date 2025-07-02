<template>
    <v-card>
      <v-alert v-if="dbError" type="error" dense>{{ dbError }}</v-alert>
      <v-card-text>
        <v-form ref="form" v-model="isValid" lazy-validation>
          <v-text-field v-model="form.name" label="Name" :rules="nameRules" required />
          <v-textarea v-model="form.description" label="Description" rows="4" auto-grow />
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-end">
        <v-btn text @click="goBack">Cancel</v-btn>
        <v-btn color="primary" :disabled="!isValid" @click="submit">Save</v-btn>
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
        form: { name: '', description: '' },
        isValid: false,
        dbError: '',
        nameRules: [(v: string) => !!v || 'Name is required']
      }
    },
    computed: {
      projectId(): number { return Number(this.$route.params.id) },
      userId(): number { return this.$store.state.auth.id }
    },
    async mounted() {
      await this.checkExisting()
    },
    methods: {
      async checkExisting() {
        try {
          const res = await axios.get(`/v1/projects/${this.projectId}/admin-perspectives/`)
          const exists = (res.data.results || res.data).some((p: any) => p.user === this.userId)
          if (exists) {
            this.$router.push(this.localePath(`/projects/${this.projectId}/admin-perspectives`))
          }
        } catch (e) {}
      },
      async submit() {
        if (!(this.$refs.form as any).validate()) return
        try {
          await axios.post(`/v1/projects/${this.projectId}/admin-perspectives/`, {
            name: this.form.name,
            description: this.form.description,
            user: this.userId
          })
          this.$router.push(this.localePath(`/projects/${this.projectId}/admin-perspectives`))
        } catch (err: any) {
          this.dbError = err.response?.data?.detail || 'Failed to create.'
        }
      },
      goBack() {
        this.$router.push(this.localePath(`/projects/${this.projectId}/admin-perspectives`))
      }
    }
  })
  </script>
  
  <style scoped>
  .v-card { max-width: 600px; margin: 20px auto; padding: 20px; }
  </style>