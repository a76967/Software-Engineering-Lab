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
          v-if="showNoAnnotationsError"
          class="mb-4"
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
          <div class="annotation-preview mb-6 pa-4">
            <h3 class="font-weight-bold">Doccana - Annotations History</h3>
            <p class="mb-4">
              <strong>Annotators:</strong>
              {{
                users
                  .filter((u) => filters.annotators.includes(u.id))
                  .map((u) => u.name)
                  .join(', ')
              }}
            </p>

            <div
              v-for="(ann, idx) in filteredAnnotations"
              :key="ann.id"
              class="annotation-item"
            >
              <div class="d-flex align-start">
                <span class="annotation-num">{{ idx + 1 }}.</span>
                <div class="flex-grow-1">
                  <span class="annotation-timestamp">{{ formatDate(ann.created_at) }}</span>
                  <span>
                    by
                    <span class="font-weight-medium">
                      {{ users.find(u=>u.id===ann.annotator)?.name||'Unknown' }}
                    </span>
                  </span>
                  <div class="annotation-text">"{{ ann.extracted_labels.text }}"</div>
                  <div class="annotation-spans">
                    <span class="annotation-span-label">Spans:</span>
                    {{ getSpansSummary(ann) }}
                  </div>
                </div>
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
    const doc = new JsPDF({ unit: 'pt', format: 'letter' })
    const margin = 40
    const maxLineWidth = doc.internal.pageSize.getWidth() - margin * 2
    const lineHeight = 14
    const pageHeight = doc.internal.pageSize.getHeight()

    let cursorY = margin

    doc.setFontSize(18)
    doc.setTextColor('#6376AB')
    doc.text('Annotations History', margin, cursorY)
    cursorY += lineHeight * 1.5

    doc.setFontSize(12)
    doc.setTextColor('#333')
    doc.text(`Perspective: ${this.filters.perspective}`, margin, cursorY)
    cursorY += lineHeight
    doc.text(`Resolution: ${this.filters.resolution}`, margin, cursorY)
    cursorY += lineHeight * 1.5

    const annotators = this.users
      .filter(u => this.filters.annotators.includes(u.id))
      .map(u => u.name)
      .join(', ')
    doc.setFontSize(12)
    doc.text(`Annotators: ${annotators}`, margin, cursorY)
    cursorY += lineHeight * 2

    this.filteredAnnotations.forEach((ann, idx) => {
      if (cursorY + 4 * lineHeight > pageHeight - margin) {
        doc.addPage()
        cursorY = margin
      }

      doc.setFontSize(11)
      doc.setTextColor('#6376AB')
      doc.text(
        `${idx + 1}. ${this.formatDate(ann.created_at)}`,
        margin,
        cursorY
      )
      doc.setTextColor('#000')
      cursorY += lineHeight

      const author = this.users.find(u => u.id === ann.annotator)?.name || 'Unknown'
      doc.setFontSize(10)
      doc.text(`by ${author}`, margin + 10, cursorY)
      cursorY += lineHeight * 1.2

      doc.setFontSize(10)
      const textLines = doc.splitTextToSize(
        `"${ann.extracted_labels.text}"`,
        maxLineWidth
      )
      doc.text(textLines, margin, cursorY)
      cursorY += textLines.length * lineHeight + lineHeight * 0.5

      const spansLine = this.getSpansSummary(ann)
      if (spansLine) {
        doc.setFontSize(10)
        doc.setTextColor('#6376AB')
        doc.text('Spans:', margin, cursorY)
        cursorY += lineHeight

        doc.setFontSize(10)
        doc.setTextColor('#000')
        const spanLines = doc.splitTextToSize(spansLine, maxLineWidth)
        doc.text(spanLines, margin + 10, cursorY)
        cursorY += spanLines.length * lineHeight + lineHeight
      }
    })

    doc.save('Doccana-Annotations-History.pdf')
  },
  },
})
</script>

<style scoped>
.annotation-preview {
  background-color: #f5f5f5;
  border-radius: 4px;
}
.annotation-item {
  margin-bottom: 16px;
}
.annotation-num {
  color: #6376AB;
  font-weight: 500;
  margin-right: 8px;
}
.annotation-timestamp {
  color: #6376AB;
  font-weight: 500;
  margin-right: 4px;
}
.annotation-text {
  margin-top: 4px;
  padding-left: 24px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
.annotation-spans {
  margin-top: 4px;
  padding-left: 24px;
}
.annotation-span-label {
  color: #6376AB;
  font-weight: 500;
  margin-right: 4px;
}
</style>