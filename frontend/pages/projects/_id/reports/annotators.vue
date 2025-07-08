<template>
  <v-container
    fluid
    class="pa-4 d-flex flex-column"
    style="min-height: calc(100vh - 64px);"
  >
    <div class="mt-12"></div>
    <h2 class="mt-4 mb-6">Annotators Report</h2>

    <v-card elevation="2" class="mb-6">
      <v-card-title>Report Filters</v-card-title>
      <v-divider/>
      <v-card-text>
        <v-form @submit.prevent="generateReport">
          <v-row dense>
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
              />
            </v-col>
          </v-row>

          <v-row>
            <v-spacer/>
            <v-btn
              color="primary"
              type="submit"
              :disabled="!filters.annotators.length"
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
          v-if="showNoData"
          class="mb-4"
          type="error"
          dismissible
          @input="showNoData = false"
        >
          <v-icon left>mdi-alert-circle</v-icon>
          No annotations found for selected annotators. Form has been reset.
        </v-alert>

        <div v-if="loading" class="text-center my-6">
          <v-progress-circular indeterminate color="primary"/>
        </div>

        <div v-else-if="historyData.length">
          <div class="annotation-preview mb-6 pa-4">
            <h3 class="font-weight-bold">Doccana – Annotations Report</h3>
            <p class="mb-4">
              <strong>Annotators:</strong>
              {{
                users
                  .filter(u => filters.annotators.includes(u.id))
                  .map(u => u.name)
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
  VContainer, VCard, VCardTitle, VDivider, VCardText,
  VForm, VRow, VCol, VAutocomplete, VBtn, VSpacer,
  VAlert, VIcon, VProgressCircular
} from 'vuetify/lib'
import { jsPDF as JsPDF } from 'jspdf'
import ApiService from '~/services/api.service'

export default Vue.extend({
  name: 'ReportsAnnotators',
  layout: 'workspace',
  components: {
    VContainer, VCard, VCardTitle, VDivider, VCardText,
    VForm, VRow, VCol, VAutocomplete, VBtn, VSpacer,
    VAlert, VIcon, VProgressCircular
  },

  data() {
    return {
      loading: false,
      showNoData: false,
      filters: {
        annotators: [] as number[]
      },
      users: [] as Array<{ id: number; name: string }>,
      allAnnotationsRaw: [] as any[],
      filteredAnnotations: [] as any[],
      historyData: [] as any[],
      headers: [
        { text: 'Timestamp', value: 'timestamp' },
        { text: 'Annotator', value: 'user' },
        { text: 'Action', value: 'action' },
        { text: 'Details', value: 'details' }
      ]
    }
  },

  computed: {
    annotatorOptions(): Array<{ id: number; name: string }> {
      const used = new Set(this.allAnnotationsRaw.map(a => a.annotator))
      return this.users.filter(u => used.has(u.id))
    }
  },

  async mounted() {
    const pid = Number(this.$route.params.id)

    try {
      const annRes = await ApiService.get('/annotations/', { params: { project: pid } })
      const raw = annRes.data.results || annRes.data
      this.allAnnotationsRaw = raw.map((a: any) => ({
        ...a,
        annotator: Number(typeof a.annotator === 'object' ? a.annotator.id : a.annotator)
      }))
    } catch {
      this.allAnnotationsRaw = []
    }

    try {
      const usrRes = await ApiService.get('/users/')
      const list = usrRes.data.results || usrRes.data
      this.users = list.map((u: any) => ({
        id: u.id,
        name: u.username || u.name || `${u.first_name||''} ${u.last_name||''}`.trim()
      }))
    } catch {
      this.users = []
    }
  },

  methods: {
    generateReport() {
      if (!this.filters.annotators.length) return
      this.loading = true

      const filtered = this.allAnnotationsRaw.filter(a =>
        this.filters.annotators.includes(a.annotator)
      )
      if (!filtered.length) {
        this.showNoData = true
        this.historyData = []
        this.filteredAnnotations = []
        this.loading = false
        return
      }

      this.filteredAnnotations = filtered
      this.historyData = filtered.map(a => ({
        timestamp: a.created_at,
        user: this.users.find(u => u.id === a.annotator)?.name || String(a.annotator),
        action: 'Created',
        details: JSON.stringify(a.extracted_labels || a.additional_info || {})
      }))
      this.loading = false
    },

    formatDate(ts: string) {
      const d = new Date(ts)
      const pad = (n: number) => n.toString().padStart(2, '0')
      return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} ` +
             `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    },

    getSpansSummary(ann: any): string {
      const text = ann.extracted_labels.text || ''
      return (ann.extracted_labels.spans || [])
        .map((s: any) => {
          const lbl = ann.extracted_labels.labelTypes.find((lt: any) => lt.id === s.label)
          const snippet = text.slice(s.start_offset, s.end_offset).trim()
          return `${lbl?.text || s.label}: ${snippet}`
        })
        .join(', ')
    },

    downloadPdf() {
      const doc = new JsPDF({ unit: 'pt', format: 'letter' })
      const margin = 40
      const maxWidth = doc.internal.pageSize.getWidth() - margin*2
      const lineH = 14
      const pageH = doc.internal.pageSize.getHeight()
      let y = margin

      doc.setFontSize(18)
      doc.setTextColor('#6376AB')
      doc.text('Annotations Report', margin, y); y += lineH*1.5

      doc.setFontSize(12)
      doc.setTextColor('#333')
      const names = this.users
        .filter(u => this.filters.annotators.includes(u.id))
        .map(u => u.name).join(', ')
      doc.text(`Annotators: ${names}`, margin, y); y += lineH*2

      this.filteredAnnotations.forEach((ann, i) => {
        if (y + 4*lineH > pageH - margin) {
          doc.addPage(); y = margin
        }
        doc.setFontSize(11)
        doc.setTextColor('#6376AB')
        doc.text(`${i+1}. ${this.formatDate(ann.created_at)}`, margin, y); y += lineH
        doc.setFontSize(10)
        doc.setTextColor('#000')
        doc.text(`by ${this.users.find(u=>u.id===ann.annotator)?.name}`, margin+10, y); y += lineH*1.2

        const tLines = doc.splitTextToSize(`"${ann.extracted_labels.text}"`, maxWidth)
        doc.text(tLines, margin, y); y += tLines.length*lineH + lineH*0.5

        const spans = this.getSpansSummary(ann)
        if (spans) {
          doc.setFontSize(10)
          doc.setTextColor('#6376AB')
          doc.text('Spans:', margin, y); y += lineH
          doc.setFontSize(10)
          doc.setTextColor('#000')
          const sLines = doc.splitTextToSize(spans, maxWidth)
          doc.text(sLines, margin+10, y); y += sLines.length*lineH + lineH
        }
      })

      doc.save('Doccana-Annotations-Report.pdf')
    }
  }
})
</script>

<style scoped>
.annotation-preview { background-color: #f5f5f5; border-radius: 4px; }
.annotation-item { margin-bottom: 16px; }
.annotation-num { color: #6376AB; font-weight: 500; margin-right: 8px; }
.annotation-timestamp { color: #6376AB; font-weight: 500; margin-right: 4px; }
.annotation-text { margin-top: 4px; padding-left: 24px; white-space: pre-wrap; }
.annotation-spans { margin-top: 4px; padding-left: 24px; }
.annotation-span-label { color: #6376AB; font-weight: 500; margin-right: 4px; }
</style>