<template>
  <v-card>
    <v-alert v-if="dbError" type="error" dense>
      {{ dbError }}
    </v-alert>

    <v-card-text>
      <v-form ref="form" v-model="isValid" lazy-validation>
        <v-select
          v-model="selectedPerspective"
          :items="adminPerspectives"
          label="Select Perspective"
          item-text="name"
          item-value="id"
          @change="fetchExtraItems"
          required
          class="bold-label"
        />
        <v-select
          v-model="form.category"
          :items="categories"
          label="Category"
          required
          class="bold-label"
        />



        <div v-for="it in extraItems" :key="it.id">
          <v-text-field
            v-if="it.data_type === 'string' || it.data_type === 'number'"
            :type="it.data_type === 'number' ? 'number' : 'text'"
            v-model="form.extra[it.name]"
            :label="`${it.name} (${it.required ? 'required' : 'optional'})`"
            :rules="it.required ? extraRules(it) : []"
          />
          <v-select
            v-else-if="it.data_type === 'boolean'"
            v-model="form.extra[it.name]"
            :items="booleanOptions"
            :label="`${it.name} (${it.required ? 'required' : 'optional'})`"
            :rules="it.required ? extraRules(it) : []"
            item-text="text"
            item-value="value"
          />
        </div>

        <v-textarea
          v-if="allowText"
          v-model="form.text"
          class="custom-input"
          :label="$t('Text')"
          counter="2000"
          rows="10"
          auto-grow
        />
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn text @click="goBack">{{ $t('generic.cancel') }}</v-btn>
      <v-btn color="primary"
             :disabled="!isValid || (extraItems.length === 0 && !allowText)"
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
        text: '',
        category: 'subjective',
        extra: {} as Record<string, any>
      },
      categories: [
        { text: this.$t('Cultural'),   value: 'cultural'  },
        { text: this.$t('Technic'),    value: 'technic'   },
        { text: this.$t('Subjective'), value: 'subjective'}
      ],
      extraItems: [] as any[],
      adminPerspectives: [] as any[],
      selectedPerspective: null as number | null,
      isValid: false,
      dbError: '',
      allowText: false,

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
    await this.checkExistingPerspective()
    const key = `allowText:${this.$route.params.id}`
    this.allowText = localStorage.getItem(key) === 'true'
    await this.fetchAdminPerspectives()
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
      if (!this.selectedPerspective) {
        this.extraItems = []
        return
      }
      try {
        const res = await this.$repositories.perspectiveField.list(
          Number(this.$route.params.id),
          this.selectedPerspective
        )
        this.extraItems = res
      } catch (e) {
        this.extraItems = []
      }
      if (!this.extraItems.length && !this.allowText) {
        this.dbError = 'Project admin has not set the items yet.'
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
      if (!this.selectedPerspective) {
        this.dbError = 'Please select a perspective.'
        return
      }
      const missing: string[] = []
      for (const it of this.extraItems) {
        if (!it.required) continue
        const val = this.form.extra[it.name]
        const rule = this.extraRules(it)[0](val)
        if (rule !== true) {
          missing.push(it.name)
        }
      }
      if (missing.length) {
        const names = missing.join(', ')
        this.dbError = `Please fill in: ${names}`
        return
      }
      const projectId = Number(this.$route.params.id)
      const userId    = this.$store.state.auth.id
      const rawText   = this.allowText ? this.form.text.trim() : ''

      const segs: string[] = []
      for (const it of this.extraItems) {
        const val = this.form.extra[it.name]
        if (val !== undefined && val !== '') {
          segs.push(`${it.name}: ${val}`)
        }
      }

      const full = rawText ? `${segs.join(', ')}. ${rawText}` : segs.join(', ')
      if (!full) {
        this.dbError = 'Project admin has not set the items yet.'
        return
      }
      const payload = {
        text:     full,
        category: this.form.category,
        user:     userId,
        admin_perspective: this.selectedPerspective
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
        // print actual validation errors
        console.error('Create perspective failed:', err.response?.data || err)
        // show first field error
        const data = err.response?.data || {}
        const firstKey = Object.keys(data)[0]
        this.dbError = Array.isArray(data[firstKey])
          ? data[firstKey][0]
          : data[firstKey] || 'Failed to create perspective.'
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
            return !isNaN(Number(v)) || `${it.name} must be a number`
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