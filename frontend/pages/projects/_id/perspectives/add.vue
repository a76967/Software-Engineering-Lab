<template>
  <v-card>
    <v-alert v-if="dbError" type="error" dense>
      {{ dbError }}
    </v-alert>

    <v-card-text>
      <v-form ref="form" v-model="isValid" lazy-validation>
        <v-select
          v-model="form.adminPerspective"
          :items="adminPerspectives"
          item-text="name"
          item-value="id"
          label="Perspective"
          readonly
          class="bold-label"
        />

        <!-- fields coming from the selected Admin Perspective -->
        <div v-for="field in extraItems" :key="field.id" class="mt-4">
          <v-text-field
            v-if="field.data_type === 'string' || field.data_type === 'number'"
            v-model="form.extra[field.name]"
            :type="field.data_type === 'number' ? 'number' : 'text'"
            :label="`${field.name}${field.required ? ' *' : ''}`"
            :rules="field.required ? extraRules(field) : []"
            :required="field.required"
          />
          <v-select
            v-else-if="field.data_type === 'boolean'"
            v-model="form.extra[field.name]"
            :items="booleanOptions"
            item-text="text"
            item-value="value"
            :label="`${field.name}${field.required ? ' *' : ''}`"
            :rules="field.required ? extraRules(field) : []"
          />
          <v-select
            v-else-if="field.data_type === 'enum'"
            v-model="form.extra[field.name]"
            :items="field.enum || []"
            :label="`${field.name}${field.required ? ' *' : ''}`"
            :rules="field.required ? extraRules(field) : []"
          />
        </div>

      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn text @click="goBack">{{ $t('generic.cancel') }}</v-btn>
      <v-btn color="primary"
             :disabled="!isValid"
             @click="submitPerspective">
        {{ $t('generic.add') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'

export default Vue.extend({
  name: 'CreatePerspective',
  layout: 'project',

  data () {
    return {
      form: {
        extra: {} as Record<string, any>,
        adminPerspective: null as number | null
      },
      extraItems: [] as any[],
      adminPerspectives: [] as any[],
      isValid: false,
      dbError: '',
      booleanOptions: [
        { text: 'Yes', value: true },
        { text: 'No',  value: false }
      ]
    }
  },

  computed: {
    ...mapGetters('auth', ['getUsername']),
    userRole (): string {
      return this.$store.state.auth.role || 'annotator'
    }
  },

  async mounted () {
    // prevent duplicate user perspective
    await this.checkExistingPerspective()
    // load the single admin perspective and its fields
    await this.fetchAdminPerspectives()
    if (this.adminPerspectives.length) {
      this.form.adminPerspective = this.adminPerspectives[0].id
      await this.fetchExtraItems()
    }
  },

  methods: {
    async fetchAdminPerspectives () {
      try {
        const res = await this.$repositories.adminPerspective.list(Number(this.$route.params.id))
        this.adminPerspectives = res
      } catch (e) {
        this.adminPerspectives = []
      }
    },

    async fetchExtraItems () {
      if (!this.form.adminPerspective) {
        this.extraItems = []
        return
      }
      try {
        this.extraItems = await this.$repositories.perspectiveField.list(
          Number(this.$route.params.id),
          this.form.adminPerspective
        )
      } catch {
        this.extraItems = []
      }
      if (!this.extraItems.length) {
        this.dbError = 'No fields defined by project admin.'
      }
    },

    async checkExistingPerspective () {
      const projectId = this.$route.params.id
      const userId    = this.$store.state.auth.id
      try {
        const list = await this.$repositories.perspective.list(projectId)
        const existing = list.find((p:any) => p.userId === userId)
        if (existing) {
          this.$router.push(
            this.localePath(`/projects/${projectId}/perspectives/edit?perspectiveId=${existing.id}`)
          )
        }
      } catch (e) {
        console.error('Failed to check existing ', e)
      }
    },

    async submitPerspective () {
      this.dbError = ''
      ;(this.$refs.form as any).validate()
      if (!this.form.adminPerspective) {
        this.dbError = 'Perspective not selected.'
        return
      }
      const missing = this.extraItems
        .filter(f => f.required && !this.form.extra[f.name])
        .map(f => f.name)
      if (missing.length) {
        this.dbError = `Please fill: ${missing.join(', ')}`
        return
      }

      const projectId = Number(this.$route.params.id)
      // compose the user‐entered values into the text field
      const text = this.extraItems
        .map(it => {
          const v = this.form.extra[it.name]
          return v !== undefined && v !== '' ? `${it.name}: ${v}` : null
        })
        .filter(Boolean)
        .join(', ')
      const payload = {
        user: this.$store.state.auth.id,
        admin_perspective: this.form.adminPerspective,
        extra: this.form.extra,
        text
      }

      try {
        await this.$repositories.perspective.create(projectId, payload)
        this.$router.push({
          path: this.localePath('/message'),
          query: {
            message: 'Perspective added successfully!',
            redirect: this.localePath(`/projects/${projectId}/perspectives`)
          }
        })
      } catch (err:any) {
        const data = err.response?.data || {}
        const key = Object.keys(data)[0]
        this.dbError = Array.isArray(data[key]) ? data[key][0] : data[key] || 'Failed to create.'
      }
    },

    extraRules(it: any) {
      return [
        (v: any) => {
          if (it.data_type === 'boolean') {
            return v === true || v === false || `${it.name} is required`
          }
          if (it.data_type === 'number') {
            if (v === null || v === undefined || v === '') {
              return `${it.name} is required`
            }
            const num = Number(v)
            if (isNaN(num)) return `${it.name} must be a number`
            if (!Number.isInteger(num)) return `${it.name} must be an integer`
            if (num < 0) return `${it.name} must be non-negative`
            return true
          }
          if (it.data_type === 'enum') {
            return !!v || `${it.name} is required`
          }
          if (it.data_type === 'enum') {
            return !!v || `${it.name} is required`
          }
          return !!v || `${it.name} is required`
        }
      ]
    },

    goBack () {
      this.$router.push(
        this.localePath(`/projects/${this.$route.params.id}/perspectives`)
      )
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
.headline {
  cursor: pointer;
  font-weight: bold;
  font-size: 1.5rem;
  display: inline-flex;
  align-items: center;
}
.headline .edit-icon {
  opacity: 0;
  transition: opacity 0.3s;
  color: inherit;
  margin-left: 8px;
}
.headline:hover .edit-icon {
  opacity: 1;
}
::v-deep .custom-input .v-input__slot {
  background-color: #f0f0f0 !important;
  border-radius: 4px;
}
::v-deep .bold-label .v-label {
  font-weight: bold;
}
</style>