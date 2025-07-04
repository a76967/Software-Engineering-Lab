<template>
  <v-card>
    <v-alert v-if="dbError" type="error" dense>
      {{ dbError }}
    </v-alert>

    <v-card-text>
      <v-form ref="form" v-model="isValid">
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
      // master lists for lookups
      countries: [] as string[],
      allowedGenders: [
        'M','F','Male','Female',
        'Masculine','Feminine','Masculino','Feminino'
      ],
      form: {
        extra: {} as Record<string, any>,
        adminPerspective: null as number | null
      },
      extraItems: [] as any[],
      adminPerspectives: [] as any[],
      booleanOptions: [
        { text: 'Yes', value: true },
        { text: 'No',  value: false }
      ],
      isValid: false,
      dbError: ''
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
    // now also fetch the master list of countries
    try {
      this.countries = await this.$axios.$get('/v1/perspectives/countries/')
    } catch (_) {
      this.countries = []
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
      // run full form validation and block save if invalid
      const formValid = (this.$refs.form as any).validate()
      if (!formValid) {
        this.dbError = 'Insert all data before saving'
        return
      }
      if (!this.form.adminPerspective) {
        this.dbError = 'Perspective not selected.'
        return
      }
      // require every field to be filled
      const missing = this.extraItems
        .filter(f => {
          const v = this.form.extra[f.name]
          return v === undefined || v === ''
        })
        .map(f => f.name)
      if (missing.length) {
        this.dbError = 'Insert all data before saving'
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
      // build a list of validator functions:
      const rules: Array<(v: any)=> true|string> = []

      // boolean is always just required
      if (it.data_type === 'boolean') {
        rules.push(v => v === true || v === false || `${it.name} is required`)
      }

      // number → integer ≥ 0, with special “Age” name hint
      else if (it.data_type === 'number') {
        // required
        rules.push(v => v!=='' && v!==null && v!==undefined || `${it.name} is required`)
        // integer check
        rules.push(v => {
          const n = Number(v)
          if (isNaN(n))         return `${it.name} must be a number`
          if (!Number.isInteger(n)) return `${it.name} must be an integer`
          if (n < 0)            return `${it.name} must be non-negative`
          return true
        })
      }

      // string → possibly country/nationality or gender
      else if (it.data_type === 'string') {
        // required
        rules.push(v => !!v || `${it.name} is required`)

        const nm = it.name.toLowerCase()
        if (['country','nationality'].includes(nm)) {
          // must match real country
          rules.push(v =>
            this.countries.includes(v)
              ? true
              : 'This country does not exist'
          )
        }
        else if (nm === 'gender') {
          // must be one of allowed genders
          rules.push(v =>
            this.allowedGenders.includes(v)
              ? true
              : `${it.name} must be one of: ${this.allowedGenders.join(', ')}`
          )
        }
      }

      // enum → just required (you already bound items to the enum list)
      else if (it.data_type === 'enum') {
        rules.push(v => !!v || `${it.name} is required`)
      }

      return rules
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