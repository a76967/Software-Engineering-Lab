<template>
  <v-card>
    <v-alert v-if="errorMessage" type="error" dense>
      {{ errorMessage }}
    </v-alert>

    <v-card-text>
      <v-form ref="form" v-model="isValid" lazy-validation>
        <v-text-field v-model="newItem.name" label="Name" required :rules="nameRules" />
        <v-select
          v-model="newItem.admin_perspective"
          :items="adminPerspectives"
          item-text="name"
          item-value="id"
          label="Admin Perspective"
          required
        />
        <v-select
          v-model="newItem.data_type"
          :items="types"
          label="Data Type"
          required
          :rules="dataTypeRules"
        />
        <v-checkbox v-model="newItem.required" label="Required" />
      </v-form>

      <v-checkbox v-model="allowText" label="Allow users to write a text" class="mt-4" />

      <!-- preview of items to be saved -->
      <v-simple-table v-if="pendingItems.length" class="mt-4">
        <thead>
          <tr>
            <th>Name</th>
            <th>Perspective</th>
            <th>Type</th>
            <th>Required</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(it, i) in pendingItems" :key="i">
            <td>{{ it.name }}</td>
            <td>{{ perspectiveName(it.admin_perspective) }}</td>
            <td>{{ it.data_type }}</td>
            <td>
              <v-icon small color="green" v-if="it.required">mdi-check</v-icon>
              <v-icon small color="red" v-else>mdi-close</v-icon>
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
        :disabled="!newItem.name || !newItem.data_type || hasPerspectives"
        @click="addItem"
      >
        Add
      </v-btn>
      <v-btn color="primary" :disabled="!canSave || hasPerspectives" class="ms-2" @click="saveAll"
        >Save</v-btn
      >
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
      items: [] as any[],
      adminPerspectives: [] as any[],
      newItem: { name: '', admin_perspective: null, data_type: '', required: false },
      types: ['string', 'number', 'boolean', 'enum'],
      pendingItems: [] as any[],
      isValid: false,
      errorMessage: '',
      allowText: false,
      originalAllowText: false,
      hasPerspectives: false,
      nameRules: [
        (v: string) => !!v || 'Name is required',
        (v: string) => {
          const dup = (this as any).items
            .concat((this as any).pendingItems)
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
      return this.pendingItems.length > 0 || this.allowText !== this.originalAllowText
    }
  },

  mounted() {
    this.checkPerspectives()
    this.fetchItems()
    this.fetchAdminPerspectives()
    this.pendingItems = []
    const key = `allowText:${this.projectId}`
    this.allowText = localStorage.getItem(key) === 'true'
    this.originalAllowText = this.allowText
  },


  methods: {
    async checkPerspectives() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/perspectives/`, {
          params: { limit: 1 }
        })
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
        } else {
          this.hasPerspectives = false
        }
      } catch {
        this.hasPerspectives = false
      }
    },
    async fetchItems() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/perspective-items/`)
        this.items = (res.data.results || res.data).map((it: any) => ({ ...it, builtin: false }))
      } catch {
        this.items = []
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
    perspectiveName(id: number | null): string {
      const p = this.adminPerspectives.find((ap: any) => ap.id === id)
      return p ? p.name : ''
    },

    addItem() {
      if (this.hasPerspectives) return
      if (!(this.$refs.form as any).validate()) return
      this.errorMessage = ''
      this.pendingItems.push({ ...this.newItem })
      this.newItem = { name: '', admin_perspective: null, data_type: '', required: false }
      ;(this.$refs.form as any).resetValidation()
    },

    cancel() {
      this.$router.push(this.localePath(`/projects/${this.projectId}/perspective-items`))
    },

    async saveAll() {
      if (this.hasPerspectives) return
      try {
        for (const it of this.pendingItems) {
          await axios.post(`/v1/projects/${this.projectId}/perspective-items/`, it)
        }
        const key = `allowText:${this.projectId}`
        localStorage.setItem(key, String(this.allowText))
        this.originalAllowText = this.allowText
        this.$router.push({
          path: this.localePath('/message'),
          query: {
            message: 'Perspective items saved!',
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