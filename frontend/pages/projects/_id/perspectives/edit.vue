<template>
  <v-card>
    <v-alert v-if="dbError" type="error" dense>
      {{ dbError }}
    </v-alert>
    <v-card-title>
      <div>
        <template v-if="editingSubject">
          <v-text-field
            v-model="form.subject"
            label="Subject"
            dense
            solo
            hide-details
            autofocus
            class="elevation-0"
            @blur="editingSubject = false"
            @keyup.enter="editingSubject = false"
          />
        </template>
        <template v-else>
          <span class="headline" @click="editingSubject = true">
            {{ form.subject || 'Perspective Title' }}
            <v-icon class="edit-icon">{{ mdiPencil }}</v-icon>
          </span>
        </template>
      </div>
    </v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="isValid" lazy-validation>
        <v-select
          v-model="form.category"
          class="custom-input"
          :items="categories"
          :label="$t('Category')"
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
      <v-spacer></v-spacer>
      <v-btn text @click="cancelEdit">{{ $t('generic.cancel') }}</v-btn>
      <v-btn color="primary" :disabled="!isValid" @click="submitEdit">
        {{ $t('generic.save') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'
import { mdiPencil } from '@mdi/js'
import { mapGetters } from 'vuex'
export default Vue.extend({
  name: 'EditPerspective',
  layout: 'project',
  data() {
    return {
      mdiPencil,
      editingSubject: false,
      isValid: false,
      form: {
        subject: '',
        text: '',
        category: 'subjective',
        extra: {} as Record<string, any>
      },
      originalForm: {
        subject: '',
        text: '',
        category: 'subjective'
      },
      categories: [] as any[],
      extraItems: [] as any[],
      selectedPerspective: null as number | null,
      booleanOptions: [
        { text: 'Yes', value: true },
        { text: 'No', value: false }
      ],
      allowText: false,
      dbError: '',
      originalText: ''
    }
  },
  computed: {
    ...mapGetters('auth', ['getUsername'])
  },
  mounted() {
    const key = `allowText:${this.$route.params.id}`
    this.allowText = localStorage.getItem(key) === 'true'
    this.loadPerspective()
    this.fetchCategories()
  },
  methods: {
    async loadPerspective() {
      const perspectiveId = this.$route.query.perspectiveId
      if (perspectiveId && this.$route.params.id) {
        try {
          const { data } = await axios.get(
            `/v1/projects/${this.$route.params.id}/perspectives/${perspectiveId}/`
          )
          this.selectedPerspective = data.admin_perspective
          this.form.subject = data.subject
          this.form.category = data.category
          this.originalText = data.text
          await this.fetchExtraItems()
          const parsed = this.parseText(data.text)
          this.form.extra = parsed.extra
          this.form.text = parsed.rawText
          this.originalForm = {
            subject: this.form.subject,
            text: this.form.text,
            category: this.form.category
          }
        } catch (error:any) {
          console.error('Erro ao buscar perspective:', error.response || error.message)
        }
      }
    },
    fetchCategories() {
      this.categories = [
        { text: this.$t('Cultural'), value: 'cultural' },
        { text: this.$t('Technic'), value: 'technic' },
        { text: this.$t('Subjective'), value: 'subjective' }
      ]
    },
    async fetchExtraItems() {
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
    },
    parseText(text: string) {
      const result = { extra: {} as Record<string, any>, rawText: '' }
      let itemsPart = text
      const dotIndex = text.indexOf('. ')
      if (dotIndex !== -1) {
        itemsPart = text.slice(0, dotIndex)
        result.rawText = text.slice(dotIndex + 2)
      }
      if (!itemsPart.trim()) return result
      const pairs = itemsPart.split(',')
      for (const seg of pairs) {
        const [name, value] = seg.split(':').map(s => s.trim())
        const it = this.extraItems.find((e:any) => e.name === name)
        if (!it) continue
        let val: any = value
        if (it.data_type === 'number') val = Number(value)
        if (it.data_type === 'boolean') val = value === 'true' || value === 'True' || value === '1'
        result.extra[name] = val
      }
      return result
    },
    combineText() {
      const rawText = this.allowText ? this.form.text.trim() : ''
      const segs: string[] = []
      for (const it of this.extraItems) {
        const val = this.form.extra[it.name]
        if (val !== undefined && val !== '') {
          segs.push(`${it.name}: ${val}`)
        }
      }
      return rawText ? `${segs.join(', ')}. ${rawText}` : segs.join(', ')
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
    submitEdit() {
      const perspectiveId = this.$route.query.perspectiveId
      if (perspectiveId && this.$route.params.id) {
        this.dbError = ''
        for (const it of this.extraItems) {
          const val = this.form.extra[it.name]
          const rule = this.extraRules(it)[0](val)
          if (rule !== true) {
            this.dbError = rule as string
            return
          }
        }
        const fullText = this.combineText()
        const patchData: any = {}
        if (this.form.subject !== this.originalForm.subject) {
          patchData.subject = this.form.subject
        }
        if (fullText !== this.originalText) {
          patchData.text = fullText
        }
        if (this.form.category !== this.originalForm.category) {
          patchData.category = this.form.category
        }
        if (Object.keys(patchData).length === 0) {
          console.log('Nenhuma alteração realizada.')
          return
        }
        axios.patch(
          `/v1/projects/${this.$route.params.id}/perspectives/${perspectiveId}/`,
          patchData
        )
          .then(() => {
            this.$router.push({
              path: '/message',
              query: {
                message: 'Perspective updated successfully!',
                redirect: `/projects/${this.$route.params.id}/perspectives`
              }
            })
          })
          .catch(error => {
            console.error('Erro ao atualizar perspective:', error.response || error.message)
            this.dbError = "Can't access our database!"
          })
      }
    },
    cancelEdit() {
      this.$router.push(this.localePath(`/projects/${this.$route.params.id}/perspectives`))
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
</style>