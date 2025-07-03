<template>
    <v-card>
      <v-alert v-if="dbError" type="error" dense>{{ dbError }}</v-alert>
      <v-card-text>
        <v-form ref="form" v-model="isValid" lazy-validation>
          <v-text-field v-model="form.name" label="Name" :rules="nameRules" required />
          <v-textarea v-model="form.description" label="Description" rows="4" auto-grow />
        </v-form>

        <v-divider class="my-4" />
        <h6 class="mb-2">Items</h6>
        <v-simple-table v-if="itemsToAdd.length" dense>
          <thead>
            <tr><th>Name</th><th>Type</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="(it,i) in itemsToAdd" :key="i">
              <td>{{ it.name }}</td>
              <td>{{ it.data_type }}</td>
              <td>
                <v-btn icon small @click="itemsToAdd.splice(i,1)">
                  <v-icon small>mdi-delete</v-icon>
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-simple-table>

        <v-row align="center" class="mt-2">
          <v-col cols="5">
            <v-text-field
              v-model="newItem.name"
              label="Item Name"
              :rules="itemNameRules"
              dense
            />
          </v-col>
          <v-col cols="5">
            <v-select
              v-model="newItem.data_type"
              :items="types"
              label="Data Type"
              :rules="itemTypeRules"
              dense
            />
          </v-col>
          <v-col cols="2">
            <v-btn
              color="primary"
              @click="addItem"
              :disabled="!newItem.name || !newItem.data_type"
            >Add</v-btn>
          </v-col>
        </v-row>
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
        nameRules: [(v: string) => !!v || 'Name is required'],

        // new items state
        types: ['string','number','boolean','enum'],
        newItem: { name: '', data_type: '' },
        itemsToAdd: [] as Array<{name:string,data_type:string}>,
        itemNameRules: [(v: string) => !!v || 'Item name required'],
        itemTypeRules: [(v: string) => !!v || 'Type required']
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

      addItem() {
        if (!this.newItem.name || !this.newItem.data_type) return
        this.itemsToAdd.push({ ...this.newItem })
        this.newItem.name = ''
        this.newItem.data_type = ''
      },

      async submit() {
        if (!(this.$refs.form as any).validate()) return
        try {
          // create perspective
          const { data: created } = await axios.post(
            `/v1/projects/${this.projectId}/admin-perspectives/`,
            {
              name: this.form.name,
              description: this.form.description,
              user: this.userId
            }
          )
          // create items
          const pid = created.id
          await Promise.all(this.itemsToAdd.map(it =>
            axios.post(
              `/v1/projects/${this.projectId}/perspective-items/`,
              { name: it.name, data_type: it.data_type, admin_perspective: pid }
            )
          ))

          this.$router.push({
            path: this.localePath('/message'),
            query: {
              message: 'Admin perspective created successfully!',
              redirect: this.localePath(
                `/projects/${this.projectId}/admin-perspectives`
              )
            }
          })
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