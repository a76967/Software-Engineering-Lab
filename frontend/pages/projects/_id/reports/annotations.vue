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
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ann, idx) in filteredAnnotations" :key="ann.id">
                <td>{{ idx + 1 }}</td>
                <td>{{ formatDate(ann.created_at) }}</td>
                <td>{{ users.find(u => u.id === ann.annotator)?.name || 'Unknown' }}</td>
                <td>{{ ann.extracted_labels.text }}</td>
                <td>{{ getSpansSummary(ann) }}</td>
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
      filteredAnnotations: [] as any[],
      users: [] as { id: number; name: string }[],
      selectedVersion: null as number | null,
      errorMessage: '' as string
    }
  },
  computed: {
    annotationOptions(): Array<{ id: number; text: string }> {
      // build list with snippet
      const opts = this.allAnnotationsRaw.map(a => {
        const txt = a.extracted_labels.text || ''
        const snippet = txt.slice(0, 50) + (txt.length > 50 ? '…' : '')
        return { id: a.id, text: `#${a.id} – ${snippet}` }
      })
      // sort by id ascending
      return opts.sort((a, b) => a.id - b.id)
    },
    annotatorOptions(): Array<{ id: number; name: string }> {
      const used = new Set(this.allAnnotationsRaw.map(a => a.annotator))
      return this.users.filter(u => used.has(u.id))
    },
    // restore dynamic Labels entirely from annotation payload:
    labelOptions(): Array<{ id: number; text: string }> {
      // pick data‐set depending on whether a report has been generated
      const src = this.filteredAnnotations.length
        ? this.filteredAnnotations
        : this.allAnnotationsRaw

      // collect all label IDs used in spans
      const usedIds = new Set<number>(
        src.flatMap(a =>
          (a.extracted_labels.spans || []).map((s: any) => s.label)
        )
      )

      // gather all labelType objects from annotations
      const allTypes = src.flatMap(a =>
        a.extracted_labels.labelTypes || []
      ) as Array<{ id: number; text: string }>

      // unique by ID
      const uniq = Array.from(
        new Map(allTypes.map(t => [t.id, t])).values()
      )

      // filter to only those used and exclude unwanted texts
      return uniq
        .filter(t => usedIds.has(t.id))
        .filter(({ text }) => text !== 'Dog' && text !== 'Cat')
        .map(({ id, text }) => ({ id, text }))
        .sort((a, b) => a.id - b.id)
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
    const [annRes, usrRes] = await Promise.all([
      ApiService.get('/annotations/', {
        params: {
          project: pid,
          limit: 1000,    // aumenta o número de resultados retornados
          offset: 0
        }
      }),
      ApiService.get('/users/')
    ])

    const raw = annRes.data.results || annRes.data
    this.allAnnotationsRaw = raw.map((a: any) => ({
      id: a.id,
      annotator: typeof a.annotator === 'object' ? a.annotator.id : a.annotator,
      extracted_labels: a.extracted_labels,
      created_at: a.created_at,
      updated_at: a.updated_at
    }))

    const list = usrRes.data.results || usrRes.data
    this.users = list.map((u: any) => ({
      id: u.id,
      name: u.username || u.name || `User ${u.id}`
    }))
  },
  methods: {
    ...mapActions('projects', ['setCurrentProject']),
    formatDate(ts: string): string {
      const d = new Date(ts)
      const pad = (n: number) => n.toString().padStart(2,'0')
      return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} `
           + `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    },
    changeVersion(id: number) {
      // update current project version in store
      this.setCurrentProject(id)
      // you can now refresh the report if desired
      // this.generateReport()
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
        // 1) filtra por Annotation IDs, se houver
        if (this.filters.annotationIds.length &&
            !this.filters.annotationIds.includes(a.id)) {
          return false
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
        this.getSpansSummary(ann)
      ])

      autoTable(doc, {
        head: [['#', 'Date', 'Annotator', 'Text', 'Spans']],
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
          // se não há filtro de labels, inclui todas; senão só as escolhidas
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