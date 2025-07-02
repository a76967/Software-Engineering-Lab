<template>
        <v-card>
      <v-alert v-if="errorMessage" type="error" dense>
        {{ errorMessage }}
      </v-alert>
  
      <v-card-text>
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
          <v-checkbox
            v-model="newItem.required"
            label="Required"
          />
        </v-form>

        <v-checkbox
          v-model="allowText"
          label="Allow users to write a text"
          class="mt-4"
        />
  
        <!-- preview of items to be saved -->
        <v-simple-table v-if="pendingItems.length" class="mt-4">
          <thead>
            <tr><th>Name</th><th>Type</th><th>Required</th></tr>
          </thead>
          <tbody>
            <tr v-for="(it,i) in pendingItems" :key="i">
              <td>{{ it.name }}</td>
              <td>{{ it.data_type }}</td>
              <td>
                <v-icon small color="green" v-if="it.required">mdi-check</v-icon>
                <v-icon small color="red"   v-else>mdi-close</v-icon>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
      </v-card-text>

      <v-card-text class="pt-0" v-if="allowText !== originalAllowText">
        <div>
          <strong>Text allowed?</strong>
          <span class="ms-2">{{ allowText ? 'Yes' : 'No' }}</span>
        </div>
      </v-card-text>
  
      <v-card-actions class="d-flex justify-end">
        <v-btn text @click="cancel">{{ $t('generic.cancel') }}</v-btn>
        <v-btn
          color="primary"
          class="ms-2"
          :disabled="!newItem.name || !newItem.data_type"
          @click="addItem"
        >
          Add
        </v-btn>
        <v-btn
        color="primary"
          :disabled="!canSave"
          class="ms-2"
          @click="saveAll"
        >Save</v-btn>
      </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import axios from 'axios'

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth','auth','setCurrentProject','isProjectAdmin'],

  data() {
    return {
      items: [] as any[],
      newItem: { name:'', data_type:'', required:false },
      types: ['string','number','boolean','enum'],
      pendingItems: [] as any[],
      isValid: false,
      errorMessage: '',
      allowText: false,
      originalAllowText: false,
      nameRules: [
        (v: string) => !!v || 'Name is required',
        (v: string) => {
          const dup = (this as any).items.concat((this as any).pendingItems)
                         .some((it: any) => it.name === v)
          return !dup || 'Name duplicated'
        }
      ],
      dataTypeRules: [
        (v: string) => !!v || 'Data Type is required',
        (v: string) => (this as any).types.includes(v) || 'Invalid Data Type'
      ]
    }
  },

  computed: {
    projectId(): number {
      return Number(this.$route.params.id)
    },
    canSave(): boolean {
      // allow save if any new items OR allowText changed
      return this.pendingItems.length > 0
        || this.allowText !== this.originalAllowText
    }
  },

  mounted() {
    this.fetchItems()
    this.pendingItems = []
    const key = `allowText:${this.projectId}`
    this.allowText = localStorage.getItem(key) === 'true'
    // remember original state
    this.originalAllowText = this.allowText
  },

  methods: {
    async fetchItems() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/perspective-items/`)
        this.items = (res.data.results||res.data).map((it:any)=>({ ...it, builtin:false }))
      } catch {
        this.items = []
      }
    },

    addItem() {
      if (!(this.$refs.form as any).validate()) return
      this.errorMessage = ''
      this.pendingItems.push({ ...this.newItem })
      this.newItem = { name:'', data_type:'', required:false }
      ;(this.$refs.form as any).resetValidation()
    },

    cancel() {
      this.$router.push(
        this.localePath(`/projects/${this.projectId}/perspective-items`)
      )
    },

    async saveAll() {
      try {
        for (const it of this.pendingItems) {
          await axios.post(
            `/v1/projects/${this.projectId}/perspective-items/`,
            it
          )
        }
        const key = `allowText:${this.projectId}`
        localStorage.setItem(key, String(this.allowText))
        this.originalAllowText = this.allowText
        this.$router.push({
          path: this.localePath('/message'),
          query: {
            message: 'Perspective items saved!',
            redirect: this.localePath(
              `/projects/${this.projectId}/perspective-items`
            )
          }
        })
      } catch (err:any) {
        const data = err.response?.data||{}
        this.errorMessage =
          data.name?.[0] ||
          data.data_type?.[0] ||
          data.required?.[0] ||
          data.non_field_errors?.join(', ') ||
          'Failed to save. Check required fields or duplicates.'
      }
    }
  }
})
</script>

<style scoped>
.v-card { max-width:800px; margin:20px auto; padding:20px; }
</style>