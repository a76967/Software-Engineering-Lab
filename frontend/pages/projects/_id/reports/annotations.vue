<template>
  <v-container
    fluid
    class="pa-4 d-flex flex-column"
    style="min-height: calc(100vh - 64px);"
  >
    <div class="mt-12"></div>
    <h2 class="mt-4 mb-6">Annotations Report</h2>

    <v-card elevation="2" class="mb-6">
      <v-card-title>Report Filters</v-card-title>
      <v-divider/>
      <v-card-text>
        <v-form @submit.prevent="generateReport">
          <!-- first row: Version, Annotation IDs, Annotators -->
          <v-row dense>
            <v-col cols="12" sm="6" md="4">
              <v-select
                v-model="selectedVersion"
                :items="versionItems"
                item-text="text"
                item-value="id"
                label="Version"
                dense
                hide-details
                @change="changeVersion"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-autocomplete
                v-model="filters.annotationIds"
                :items="annotationOptions"
                item-text="text"
                item-value="id"
                label="Annotations"
                multiple
                clearable
                dense
                hide-details
                :menu-props="{
                  'max-height': '200px',
                  contentClass: 'annotation-menu__content'
                }"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-autocomplete
                v-model="filters.annotators"
                :items="annotatorOptions"
                item-text="name"
                item-value="id"
                label="Annotators"
                multiple
                clearable
                dense
                hide-details
              />
            </v-col>
          </v-row>
          <!-- second row: Labels aligned under first columns -->
          <v-row dense>
            <v-col cols="12" sm="6" md="4">
              <v-select
                v-model="filters.labels"
                :items="labelOptions"
                item-text="text"
                item-value="id"
                label="Labels"
                multiple
                clearable
                dense
                hide-details
              />
            </v-col>
          </v-row>
          <v-row>
            <v-spacer/>
            <v-btn color="primary" type="submit">Generate Report</v-btn>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <v-card elevation="2" class="mb-6">
      <v-card-title>Preview</v-card-title>
      <v-divider/>
      <v-card-text>
        <v-alert
          v-if="errorMessage"
          dense
          type="error"
          class="mb-4"
        >
          {{ errorMessage }}
        </v-alert>
        <div v-if="loading" class="text-center my-6">
          <v-progress-circular indeterminate color="primary"/>
        </div>
        <div v-else-if="filteredAnnotations.length">
          <v-simple-table dense class="annotation-preview mb-6">
            <thead>
              <tr>
                <th>#</th>
                <th>Date</th>
                <th>Annotator</th>
                <th>Text</th>
                <th>Spans</th>
                <th>Labels</th>
                <th>Perspective</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ann, idx) in filteredAnnotations" :key="ann.id">
                <td>{{ idx + 1 }}</td>
                <td>{{ formatDate(ann.created_at) }}</td>
                <td>{{ users.find(u => u.id === ann.annotator)?.name || 'Unknown' }}</td>
                <td>{{ ann.extracted_labels.text }}</td>
                <td>{{ getSpansSummary(ann) }}</td>
                <td>{{ getLabelNames(ann) }}</td>
                <td>{{ getPerspectiveLabel(ann) }}</td>
              </tr>
            </tbody>
          </v-simple-table>
          <v-btn color="primary" @click="downloadPdf">Download PDF</v-btn>
        </div>
        <div v-else class="text-center grey--text my-6">
          No annotations. Adjust filters and click “Generate Report.”
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapActions } from 'vuex'
import { jsPDF as JsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import {
  VContainer, VCard, VCardTitle, VDivider, VCardText,
  VForm, VRow, VCol, VAutocomplete, VSelect,
  VBtn, VSpacer, VProgressCircular, VAlert, VSimpleTable
} from 'vuetify/lib'

import ApiService from '~/services/api.service'

export default Vue.extend({
  name: 'ReportsAnnotationsGeneral',
  components: {
    VContainer, VCard, VCardTitle, VDivider, VCardText,
    VForm, VRow, VCol, VAutocomplete, VSelect,
    VBtn, VSpacer, VProgressCircular, VAlert, VSimpleTable
  },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data() {
    return {
      loading: false,
      filters: {
        annotationIds: [] as number[],
        annotators: [] as number[],
        labels: [] as number[]      // agora array
      },
      allAnnotationsRaw: [] as any[],
      allSpans: [] as { id: number; snippet: string }[],
      filteredAnnotations: [] as any[],
      users: [] as { id: number; name: string }[],
      allLabels: [] as { id: number; text: string }[],
      perspectives: [] as any[],
      perspectiveMap: {} as Record<number, any[]>,
      selectedVersion: null as number | null,
      errorMessage: '' as string
    }
  },
  computed: {
    annotationOptions(): Array<{ id: number; text: string }> {
      const opts = this.allSpans.map(s => {
        const snippet = s.snippet.slice(0, 50) + (s.snippet.length > 50 ? '…' : '')
        return { id: s.id, text: `#${s.id} – ${snippet}` }
      })
      return opts.sort((a, b) => a.id - b.id)
    },
    annotatorOptions(): Array<{ id: number; name: string }> {
      return this.users
    },
    // dynamic labels dropdown
      labelOptions(): Array<{ id: number; text: string }> {
      return (this.allLabels || []).map(l => ({ id: l.id, text: l.text }))
      },
    currentProject(): any {
      return this.$store.getters['projects/currentProject']
    },
    versionItems(): Array<{ id: number; text: string }> {
      const p = this.currentProject as any
      return p && p.id
        ? [{ id: p.id, text: `Version ${p.versionNumber}` }]
        : []
    }
  },
  watch: {
    currentProject: {
      handler(p) {
        if (p && p.id) {
          this.selectedVersion = p.id
        }
      },
      immediate: true
    },
    selectedVersion(val) {
      if (val) {
        this.changeVersion(val)
      }
    }
  },
  async mounted() {
    const pid = Number(this.$route.params.id)
    await this.loadData(pid)
  },
  methods: {
    ...mapActions('projects', ['setCurrentProject']),
    async loadData(pid: number) {
      const [annRes, usrRes, lblRes, perRes, exRes] = await Promise.all([
        ApiService.get('/annotations/', {
          params: {
            project: pid,
            limit: 1000,    // aumenta o número de resultados retornados
            offset: 0
          }
        }),
        ApiService.get(`/projects/${pid}/members`),
        ApiService.get(`/projects/${pid}/span-types`),
        ApiService.get(`/projects/${pid}/perspectives/`, { params: { limit: 1000 } }),
        this.$services.example.list(String(pid), { limit: '1000', offset: '0', q: '', isChecked: '', ordering: '' })
      ])

      const raw = annRes.data.results || annRes.data
      this.allAnnotationsRaw = raw.map((a: any) => ({
        id: a.id,
        dataset_item_id: a.dataset_item_id,
        annotator: typeof a.annotator === 'object' ? a.annotator.id : a.annotator,
        extracted_labels: a.extracted_labels,
        created_at: a.created_at,
        updated_at: a.updated_at
      }))

      const list = usrRes.data.results || usrRes.data
      this.users = list.map((m: any) => ({
        id: m.user,
        name: m.username || `User ${m.user}`
      }))

      const labelsList = lblRes.data.results || lblRes.data || []
      this.allLabels = labelsList.map((l: any) => ({ id: l.id, text: l.text }))

      const examples = exRes.items || []
      const spanPromises = examples.map((ex: any) =>
        this.$services.sequenceLabeling
          .list(String(pid), ex.id)
          .then(spans => spans.map((s: any) => ({
            id: s.id,
            snippet: (ex.text || '').slice(s.startOffset, s.endOffset)
          })))
      )
      const spanResults = await Promise.all(spanPromises)
      this.allSpans = spanResults.flat()

      const pers = perRes.data.results || perRes.data || []
      this.perspectives = pers
      const map: Record<number, any[]> = {}
      pers.forEach((p: any) => {
        (p.linkedAnnotations || []).forEach((la: any) => {
          const id = typeof la === 'object' ? la.id : la
          if (id === undefined || id === null) return
          if (!map[id]) map[id] = []
          map[id].push(p)
        })
      })
    this.perspectiveMap = map
  },
    formatDate(ts: string): string {
      const d = new Date(ts)
      const pad = (n: number) => n.toString().padStart(2,'0')
      return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} `
           + `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    },
    async changeVersion(id: number) {
      // update current project version in store
      this.setCurrentProject(id)
      // reload annotations and perspectives for selected version
      await this.loadData(id)
    },
    generateReport() {
      // ensure all filters are selected
      if (!this.filters.annotationIds.length ||
          !this.filters.annotators.length ||
          !this.filters.labels.length) {
        this.errorMessage = 'Please select all the filters.'
        this.filteredAnnotations = []
        this.loading = false
        return
      }
      this.errorMessage = ''
      this.loading = true
      this.filteredAnnotations = this.allAnnotationsRaw.filter(a => {
        // 1) filter by selected span IDs
        if (this.filters.annotationIds.length) {
          const spanIds = (a.extracted_labels.spans || []).map((s: any) => s.id)
          if (!spanIds.some((id: number) => this.filters.annotationIds.includes(id))) {
            return false
          }
        }
        // 2) filtra por Annotators, se houver
        if (this.filters.annotators.length &&
            !this.filters.annotators.includes(a.annotator)) {
          return false
        }
        // 3) filtra por Labels selecionadas
        if (this.filters.labels.length) {
          const spans = a.extracted_labels.spans || []
          // mantém se tiver pelo menos 1 das labels escolhidas
          if (!spans.some((s: any) => this.filters.labels.includes(s.label))) {
            return false
          }
        }
        return true
      })
      this.loading = false
    },
    downloadPdf() {
      const doc = new JsPDF({ unit: 'pt', format: 'letter' })
      const margin = 40
      let startY = margin

      doc.setFontSize(18).setTextColor('#333')
      doc.text('Annotations Report', margin, startY)
      startY += 20

      if (this.filters.annotationIds.length) {
        doc.setFontSize(12).setTextColor('#000')
        doc.text(`IDs: ${this.filters.annotationIds.join(', ')}`, margin, startY)
        startY += 14
      }
      if (this.filters.annotators.length) {
        const names = this.users
          .filter(u => this.filters.annotators.includes(u.id))
          .map(u => u.name)
          .join(', ')
        doc.text(`Annotators: ${names}`, margin, startY)
        startY += 14
      }
      if (this.filters.labels.length) {
        const lbls = this.filters.labels
          .map(id => this.labelOptions.find(l => l.id === id)?.text || id)
          .join(', ')
        doc.text(`Labels: ${lbls}`, margin, startY)
        startY += 14
      }
      startY += 10

      const rows = this.filteredAnnotations.map((ann, idx) => [
        idx + 1,
        this.formatDate(ann.created_at),
        this.users.find(u => u.id === ann.annotator)?.name || 'Unknown',
        ann.extracted_labels.text,
        this.getSpansSummary(ann),
        this.getLabelNames(ann),
        this.getPerspectiveLabel(ann)
      ])

      autoTable(doc, {
        head: [['#', 'Date', 'Annotator', 'Text', 'Spans', 'Labels', 'Perspective']],
        body: rows,
        startY,
        styles: { fontSize: 10 },
        headStyles: { fillColor: [99, 118, 171] }
      })

      doc.save('Annotations-Report.pdf')
    },
    getSpansSummary(ann: any): string {
      const txt = ann.extracted_labels.text || ''
      // aplica filtro de labels selecionadas (se houver)
      const spans = (ann.extracted_labels.spans || [])
        .filter((s: any) =>
          !this.filters.labels.length || this.filters.labels.includes(s.label)
        )
      return spans
        .map((s: any) => {
          const lbl = ann.extracted_labels.labelTypes
            .find((lt: any) => lt.id === s.label)
          const snippet = txt.slice(s.start_offset, s.end_offset).trim()
          return `${lbl?.text || s.label}: ${snippet}`
        })
        .join(', ')
      },
    getLabelNames(ann: any): string {
      const spans = ann.extracted_labels.spans || []
      const types = ann.extracted_labels.labelTypes || []
      const names = spans.map((s: any) => {
        const t = types.find((lt: any) => lt.id === s.label)
        return t ? t.text : s.label
      })
      return Array.from(new Set(names)).join(', ')
    },
    getPerspectiveLabel(ann: any): string {
      const arr = this.perspectiveMap[ann.dataset_item_id] || []
      if (!arr.length) return '—'
      return arr.map((p: any) => p.subject || p.text || `#${p.id}`).join(', ')
    }
  }
})
</script>

<style scoped>
.annotation-preview    { background: #f5f5f5; border-radius: 4px; }
.annotation-item       { margin-bottom: 16px; }
.annotation-num        { font-weight: 500; margin-right: 12px; }
.annotation-timestamp  { color: #6376AB; font-weight: 500; margin-right: 4px; }
.annotation-text       { margin-top: 4px; padding-left: 24px;
  white-space: pre-wrap; word-wrap: break-word; }
.annotation-spans      { margin-top: 4px; padding-left: 24px; }
.annotation-span-label { color: #6376AB; font-weight: 500; margin-right: 4px; }
.annotation-menu__content {
  max-height: 200px !important;
  overflow-y: auto !important;
}
</style>