<template>
  <v-card>
    <v-alert v-if="dbError" type="error" dense>
      {{ dbError }}
    </v-alert>

    <v-card-text>
      <v-form ref="form" v-model="isValid" lazy-validation>
        <v-select
          v-model="form.category"
          :items="categories"
          label="Category"
          required
          class="bold-label"
        />

        <v-text-field
          v-model.number="form.age"
          type="number"
          label="Age (required)"
          :rules="ageRules"
          min="0"
          max="100"
          required
        />

        <v-select
          v-model="form.gender"
          :items="['M', 'F']"
          label="Gender (required)"
          required
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
          v-model="form.text"
          class="custom-input"
          :label="$t('Text')"
          counter="2000"
          rows="10"
          auto-grow
          required
        />
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn text @click="goBack">{{ $t('generic.cancel') }}</v-btn>
      <v-btn color="primary" :disabled="!isValid" @click="submitPerspective">
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
        age: null as number | null,
        gender: '',
        extra: {} as Record<string, any>
      },
      categories: [
        { text: this.$t('Cultural'),   value: 'cultural'  },
        { text: this.$t('Technic'),    value: 'technic'   },
        { text: this.$t('Subjective'), value: 'subjective'}
      ],
      extraItems: [] as any[],
      isValid: false,
      dbError: '',

      ageRules: [
        (v: number) => v !== null && v !== undefined || 'Age is required',
        (v: number) => Number.isInteger(v) || 'Age must be an integer',
        (v: number) => v >= 0 || 'Age can’t be below 0',
        (v: number) => v <= 100 || 'Age can’t be above 100'
      ],

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
    await this.fetchExtraItems()
  },

  methods: {
    async fetchExtraItems () {
      try {
        const res = await this.$repositories.perspectiveField.list(Number(this.$route.params.id))
        this.extraItems = res
      } catch (e) {
        this.extraItems = []
      }
    },
    parseBirthday (txt: string) {
      const m = txt.match(/\b(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b/)
      if (!m) return undefined
      let d   = parseInt(m[1], 10)
      let mth = parseInt(m[2], 10)
      let y   = parseInt(m[3], 10)
      if (y < 100) y += y >= 30 ? 1900 : 2000
      if (d > 12 && mth <= 12) {
        [d, mth] = [mth, d]
      }
      const date = new Date(y, mth - 1, d)
      return isNaN(date.getTime()) ? undefined : date
    },

    calcAge (born: Date) {
      const today = new Date()
      let age = today.getFullYear() - born.getFullYear()
      const m = today.getMonth() - born.getMonth()
      if (m < 0 || (m === 0 && today.getDate() < born.getDate())) age--
      return age
    },

    extractInfo (_text: string) {
      let age, gender, country, generation;
      return { age, gender, country, generation }
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
      const ageError = this.ageRules.map(r => r(this.form.age as number))
                             .find(msg => msg !== true)
      if (ageError) {
        this.dbError = ageError as string
        return
      }
      for (const it of this.extraItems) {
        const val = this.form.extra[it.name]
        const rule = this.extraRules(it)[0](val)
        if (rule !== true) {
          this.dbError = rule as string
          return
        }
      }
      const projectId = Number(this.$route.params.id)
      const userId    = this.$store.state.auth.id
      const rawText   = this.form.text.trim()

      if (!this.form.age || !this.form.gender) {
        this.dbError = 'Age and gender must be specified.'
        return
      }

      const segs = [
        `Age: ${this.form.age}`,
        `Gender: ${this.form.gender}`
      ]
      for (const it of this.extraItems) {
        const val = this.form.extra[it.name]
        if (val !== undefined && val !== '') {
          segs.push(`${it.name}: ${val}`)
        }
      }

      const full = rawText ? `${segs.join(', ')}. ${rawText}` : segs.join(', ')
      const payload = {
        text:     full,
        category: this.form.category,
        user:     userId
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
            return v !== null && v !== undefined && v !== '' || `${it.name} is required`
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