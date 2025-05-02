<template>
  <v-container
    fluid
    class="pa-4 d-flex flex-column"
    style="min-height: calc(100vh - 64px);"
  >
    <div class="mt-12"></div>
    <h2 class="mt-4 mb-6">Annotations History</h2>

    <v-card elevation="2" class="mb-6">
      <v-card-title>History Filters</v-card-title>
      <v-divider/>
      <v-card-text>
        <v-form @submit.prevent="generateReport">
          <v-row dense>
            <v-col cols="12" sm="6">
              <v-menu
                v-model="dateMenu"
                :close-on-content-click="false"
                offset-y
                max-width="290"
              >
                <template #activator="{ on, attrs }">
                  <v-text-field
                    v-model="filters.dateRangeText"
                    label="Date Range"
                    readonly
                    clearable
                    v-bind="attrs"
                    v-on="on"
                  />
                </template>

                <v-card>
                  <v-date-picker
                    v-model="filters.dateRange"
                    range
                    scrollable
                    color="primary"
                    header-color="primary lighten-2"
                    first-day-of-week="1"
                    @change="updateDateText"
                  >
                    <template #title>
                      <div class="subtitle-1 font-weight-medium pa-4">
                        {{ filters.dateRangeText || 'Select date range' }}
                      </div>
                    </template>
                    <template #selection/>
                  </v-date-picker>

                  <v-card-actions>
                    <v-spacer/>
                    <v-btn text @click="dateMenu = false">Cancel</v-btn>
                    <v-btn text @click="dateMenu = false">OK</v-btn>
                  </v-card-actions>
                </v-card>
              </v-menu>
            </v-col>

            <v-col cols="12" sm="6">
              <v-autocomplete
                v-model="filters.annotators"
                :items="annotatorOptions"
                item-text="name"
                item-value="id"
                label="Annotators"
                multiple
                clearable
                no-data-text="No annotators available"
                loading-text="Loading…"
              />
            </v-col>

            <v-col cols="12" sm="6">
              <v-select
                v-model="filters.perspective"
                :items="perspectives"
                label="Perspective"
                clearable
              />
            </v-col>

            <v-col cols="12" sm="6">
              <v-select
                v-model="filters.resolution"
                :items="resolutionStates"
                label="Resolution State"
                clearable
              />
            </v-col>
          </v-row>

          <v-row>
            <v-spacer/>
            <v-btn
              color="primary"
              type="submit"
              :disabled="!canGenerate"
            >
              Generate Report
            </v-btn>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <v-card elevation="2">
      <v-card-title>Results</v-card-title>
      <v-divider/>
      <v-card-text>
        <v-alert
          class="mb-4"
          v-if="showNoAnnotationsError"
          type="error"
          dismissible
          @input="showNoAnnotationsError = false"
        >
          <v-icon left>mdi-alert-circle</v-icon>
          No annotations were found for the selected filters. Form has been reset.
        </v-alert>

        <div v-if="loading" class="text-center my-6">
          <v-progress-circular indeterminate color="primary"/>
        </div>

        <div v-else-if="historyData.length">
          <div class="mb-6 pa-4 grey lighten-4">
            <h3 class="font-weight-bold">Doccana – Annotations History</h3>
            <p class="mb-4">
              <strong>Annotators:</strong>
              {{
                users
                  .filter((u) => filters.annotators.includes(u.id))
                  .map((u) => u.name)
                  .join(', ')
              }}
            </p>
            <div v-for="ann in filteredAnnotations" :key="ann.id" class="mb-3">
              <strong>{{ formatDate(ann.created_at) }}</strong>
              by
              <span class="font-weight-medium">
                {{ users.find((u) => u.id === ann.annotator)?.name || 'Unknown' }}
              </span>
              :
              <span class="text-justify">"{{ ann.extracted_labels.text }}"</span>

              <div class="mt-1">
                <strong>Spans:</strong>
                {{ getSpansSummary(ann) }}
              </div>
            </div>
          </div>

          <v-btn color="primary" class="mb-4" @click="downloadPdf">
            Download PDF
          </v-btn>
        </div>
        <div v-else class="text-center grey--text my-6">
          No entries. Adjust filters and click “Generate Report.”
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import {
  VContainer,
  VCard,
  VCardTitle,
  VDivider,
  VCardText,
  VForm,
  VRow,
  VCol,
  VMenu,
  VDatePicker,
  VTextField,
  VAutocomplete,
  VSelect,
  VBtn,
  VSpacer,
  VCardActions,
  VAlert,
  VIcon
} from 'vuetify/lib'

import { jsPDF as JsPDF } from 'jspdf'
import ApiService from '~/services/api.service'

export default Vue.extend({
  name: 'ReportsHistory',
  components: {
    VContainer,
    VCard,
    VCardTitle,
    VDivider,
    VCardText,
    VForm,
    VRow,
    VCol,
    VMenu,
    VDatePicker,
    VTextField,
    VAutocomplete,
    VSelect,
    VBtn,
    VSpacer,
    VCardActions,
    VAlert,
    VIcon
  },
  layout: 'workspace',
  data() {
    return {
      loading: false,
      dateMenu: false as boolean,
      filters: {
        dateRange: [] as string[],
        dateRangeText: '',
        annotators: [] as number[],
        perspective: '',
        resolution: ''
      },
      users: [] as Array<{ id: number; name: string }>,
      perspectives: ['Portugal', 'Generation X', 'Generation Y', 'Generation Z'],
      resolutionStates: ['Before Rules', 'After Rules'],
      allAnnotationsRaw: [] as any[],
      filteredAnnotations: [] as Array<any>,
      historyData: [] as any[],
      headers: [
        { text: 'Timestamp', value: 'timestamp' },
        { text: 'Annotator', value: 'user' },
        { text: 'Action', value: 'action' },
        { text: 'Details', value: 'details' },
        { text: 'Perspective', value: 'perspective' }
      ],
      showNoAnnotationsError: false as boolean
    }
  },
  computed: {
    annotatorOptions(): Array<{ id: number; name: string }> {
      const used = new Set(this.allAnnotationsRaw.map(a => a.annotator))
      return this.users.filter(u => used.has(u.id))
    },
    canGenerate(): boolean {
      return (
        this.filters.dateRange.length === 2 &&
        this.filters.annotators.length > 0 &&
        !!this.filters.perspective &&
        !!this.filters.resolution
      )
    }
  },
  async mounted() {
    const pid = Number(this.$route.params.id)

    try {
      const annRes = await ApiService.get('/annotations/', { params: { project: pid } })
      const raw = annRes.data.results || annRes.data
      this.allAnnotationsRaw = raw.map((a: any) => ({
        ...a,
        annotator: Number(
          typeof a.annotator === 'object' ? a.annotator.id : a.annotator
        )
      }))
    } catch (e) {
      console.error('Failed to load annotations:', e)
      this.allAnnotationsRaw = []
    }

    try {
      const usrRes = await ApiService.get('/users/')
      const list = usrRes.data.results || usrRes.data
      this.users = list.map((u: any) => ({
        id:   u.id,
        name: u.username || u.name || `${u.first_name||''} ${u.last_name||''}`.trim()
      }))
    } catch (e) {
      console.error('Failed to load users:', e)
      this.users = []
    }
  },
  methods: {
    updateDateText(newRange: string[]) {
      let [start, end] = newRange
      if (end < start) [start, end] = [end, start]
      this.filters.dateRange = [start, end]
      const fmt = (d: string) =>
        new Date(d).toLocaleDateString(undefined, {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        })
      this.filters.dateRangeText = `${fmt(start)} → ${fmt(end)}`
    },
    generateReport() {
      if (!this.canGenerate) return
      this.loading = true
      const [start, end] = this.filters.dateRange
      const filtered = this.allAnnotationsRaw.filter(a => {
        const d = a.created_at.slice(0,10)
        if (start && d < start) return false
        if (end && d > end) return false
        if (this.filters.annotators.length &&
            !this.filters.annotators.includes(a.annotator)
        ) return false
        return true
      })

      if (filtered.length === 0) {
        this.showNoAnnotationsError = true
        this.clearForm()
        this.loading = false
        return
      }

      this.filteredAnnotations = filtered

      this.historyData = filtered.map(a => ({
        timestamp: a.created_at,
        user: this.users.find(u=>u.id===a.annotator)?.name||String(a.annotator),
        action: 'Created',
        details: JSON.stringify(a.extracted_labels||a.additional_info||{}),
        perspective: this.filters.perspective||'All'
      }))

      this.loading = false
    },
    clearForm() {
      this.filters.dateRange = []
      this.filters.dateRangeText = ''
      this.filters.annotators = []
      this.filters.perspective = ''
      this.filters.resolution = ''
      this.filteredAnnotations = []
      this.historyData = []
    },
    formatDate(ts: string): string {
      const d = new Date(ts)
      const pad = (n: number) => n.toString().padStart(2,'0')
      return [
        pad(d.getDate()),
        pad(d.getMonth()+1),
        d.getFullYear()
      ].join('/') + ' ' + [
        pad(d.getHours()),
        pad(d.getMinutes()),
        pad(d.getSeconds())
      ].join(':')
    },
    getSpansSummary(ann: any): string {
      const text = ann.extracted_labels.text || ''
      return (ann.extracted_labels.spans || [])
        .map((s: any) => {
          const label = ann.extracted_labels.labelTypes
            .find((lt: any) => lt.id === s.label)
          const snippet = text.slice(s.start_offset, s.end_offset).trim()
          return `${label?.text || s.label}: ${snippet}`
        })
        .join(', ')
    },
    downloadPdf() {
      const doc = new JsPDF()

      const title = [
        'Annotations History',
        `Perspective: ${this.filters.perspective}`,
        `Resolution: ${this.filters.resolution}`,
      ].join(' – ')
      doc.setFontSize(18)
      doc.setTextColor('#1976D2')
      doc.text(title, 14, 20)

      const annotators = this.users
        .filter((u) => this.filters.annotators.includes(u.id))
        .map((u) => u.name)
        .join(', ')
      doc.setFontSize(12)
      doc.setTextColor(0)
      doc.text(`Annotators: ${annotators}`, 14, 30)

      let y = 40
      this.filteredAnnotations.forEach((ann, index) => {
        if (y > 270) {
          doc.addPage()
          y = 20
        }

        doc.setFontSize(10)
        doc.setTextColor('#1976D2')
        doc.text(`${index + 1}. ${this.formatDate(ann.created_at)}`, 14, y)
        doc.setTextColor(0)
        doc.text(` by ${this.users.find((u) => u.id === ann.annotator)?.name || 'Unknown'}`, 80, y)

        y += 6
        doc.setFontSize(10)
        doc.setTextColor(0)
        const text = doc.splitTextToSize(`"${ann.extracted_labels.text}"`, 180)
        doc.text(text, 14, y)
        y += text.length * 6

        if (ann.extracted_labels.spans?.length) {
          doc.setFontSize(10)
          doc.setTextColor('#1976D2')
          doc.text('Spans:', 14, y)
          y += 6
          doc.setFontSize(10)
          doc.setTextColor(0)
          const spans = this.getSpansSummary(ann)
          const spanLines = doc.splitTextToSize(spans, 180)
          doc.text(spanLines, 14, y)
          y += spanLines.length * 6
        }

        y += 4
      })

      doc.save('DoccanaAnnotationHistory.pdf')
    },
  },
})
</script>

<style scoped>
</style>