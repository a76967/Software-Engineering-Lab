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
          <v-row dense>
            <v-col cols="12" sm="6" md="4">
              <v-select
                v-model="selectedVersion"
                :items="versionItems"
                item-text="text"
                item-value="id"
                label="Version"
                hide-details
                dense
                @change="changeVersion"
              />
            </v-col>
            <!-- Annotation IDs with text snippet -->
            <v-col cols="12" sm="6" md="4">
              <v-autocomplete
                v-model="filters.annotationIds"
                :items="annotationOptions"
                item-text="text"
                item-value="id"
                label="Annotation IDs"
                multiple
                clearable
                :menu-props="{
                  'max-height': '200px',
                  contentClass: 'annotation-menu__content'
                }"
              />
            </v-col>

            <!-- Annotators -->
            <v-col cols="12" sm="6" md="4">
              <v-autocomplete
                v-model="filters.annotators"
                :items="annotatorOptions"
                item-text="name"
                item-value="id"
                label="Annotators"
                multiple
                clearable
              />
            </v-col>

            <!-- Labels agora múltiplos -->
            <v-col cols="12" sm="6" md="4">
              <!-- permite selecionar várias -->
              <v-select
                v-model="filters.labels"
                :items="labelOptions"
                item-text="text"
                item-value="id"
                label="Labels"
                multiple
                clearable
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
        <div v-if="loading" class="text-center my-6">
          <v-progress-circular indeterminate color="primary"/>
        </div>
        <div v-else-if="filteredAnnotations.length">
          <div class="annotation-preview mb-6 pa-4">
            <div
              v-for="(ann, idx) in filteredAnnotations"
              :key="ann.id"
              class="annotation-item"
            >
              <div class="d-flex align-start">
                <span class="annotation-num">{{ idx + 1 }}.</span>
                <div class="flex-grow-1">
                  <span class="annotation-timestamp">
                    {{ formatDate(ann.created_at) }}
                  </span>
                  <span>
                    by
                    <strong>
                      {{
                        users.find(u => u.id === ann.annotator)?.name
                        || 'Unknown'
                      }}
                    </strong>
                  </span>
                  <div class="annotation-text pa-2">
                    "{{ ann.extracted_labels.text }}"
                  </div>
                  <div class="annotation-spans">
                    <span class="annotation-span-label">Spans:</span>
                    {{ getSpansSummary(ann) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
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
import {
  VContainer, VCard, VCardTitle, VDivider, VCardText,
  VForm, VRow, VCol, VAutocomplete, VSelect,
  VBtn, VSpacer, VProgressCircular
} from 'vuetify/lib'

import ApiService from '~/services/api.service'

export default Vue.extend({
  name: 'ReportsAnnotationsGeneral',
  components: {
    VContainer, VCard, VCardTitle, VDivider, VCardText,
    VForm, VRow, VCol, VAutocomplete, VSelect,
    VBtn, VSpacer, VProgressCircular
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
      selectedVersion: null as number | null
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
    // dynamic labels dropdown
    labelOptions(): Array<{ id: number; text: string }> {
      // pick data‐set depending on whether a report has been generated
      const src = this.filteredAnnotations.length
        ? this.filteredAnnotations
        : this.allAnnotationsRaw

      // only include labels that actually occur in spans
      const usedSpanIds = new Set<number>(
        src.flatMap(a =>
          (a.extracted_labels.spans || []).map((s: any) => s.label)
        )
      )
      const types = src
        .flatMap(a => a.extracted_labels.labelTypes || [])
        .filter((t: any) => usedSpanIds.has(t.id))

      // dedupe & exclude unwanted
      const uniq = Array.from(
        new Map(types.map((t: any) => [t.id, t])).values()
      )
      return uniq
        .filter((t: any) => t.text !== 'Dog' && t.text !== 'Cat')
        .map((t: any) => ({ id: t.id, text: t.text }))
    },
    projectVersions(): Array<any> {
      return this.$store.getters['projects/projectVersions']
    },
    versionItems(): Array<{ id: number; text: string }> {
      return this.projectVersions.map(v => ({ id: v.id, text: `Version ${v.versionNumber}` }))
    }
  },
  watch: {
    projectVersions: {
      handler() {
        const versions = this.projectVersions as Array<any>
        if (!this.selectedVersion && versions.length) {
          this.selectedVersion = versions[0].id
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
      const version = this.projectVersions.find(v => v.id === id)
      const number = version ? version.versionNumber : ''
      this.setCurrentProject(id)
      this.$router.push({
        path: '/message',
        query: {
          message: `Changing to Version ${number} of the project`,
          redirect: `/projects/${id}/reports/annotations`
        }
      })
    },
    generateReport() {
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
      const m = 40
      const lh = 14
      const ph = doc.internal.pageSize.getHeight()
      let y = m

      doc.setFontSize(18).setTextColor('#333')
      doc.text('Annotations Report', m, y); y += lh * 1.5

      if (this.filters.annotationIds.length) {
        doc.setFontSize(12).setTextColor('#000')
        doc.text(`IDs: ${this.filters.annotationIds.join(', ')}`, m, y); y += lh
      }
      if (this.filters.annotators.length) {
        const names = this.users
          .filter((u) => this.filters.annotators.includes(u.id))
          .map((u) => u.name)
          .join(', ')
        doc.setFontSize(12).setTextColor('#000')
        doc.text(`Annotators: ${names}`, m, y)
        y += lh
      }
      if (this.filters.labels.length) {
        const lbls = this.filters.labels
          .map((id) => this.labelOptions
            .find((l: { id: number; text: string }) => l.id === id)?.text || id)
          .join(', ')
        doc.text(`Labels: ${lbls}`, m, y)
        y += lh
      }
      y += lh

      this.filteredAnnotations.forEach((ann, i) => {
        if (y + 6 * lh > ph - m) { doc.addPage(); y = m }
        doc.setFontSize(10).setTextColor('#6376AB')
        doc.text(`${i+1}. ${this.formatDate(ann.created_at)}`, m, y)
        y += lh

        const author = this.users.find(u=>u.id===ann.annotator)?.name || 'Unknown'
        doc.setFontSize(10).setTextColor('#000')
        doc.text(`by ${author}`, m + 10, y)
        y += lh

        const snippet = ann.extracted_labels.text.slice(0, 100) +
          (ann.extracted_labels.text.length > 100 ? '…' : '')
        doc.setFontSize(11).setTextColor('#333')
        doc.text(snippet, m + 20, y)
        y += lh * 1.5

        // print spans summary
        const spansLine = this.getSpansSummary(ann)
        if (spansLine) {
          // label
          doc.setFontSize(10).setTextColor('#6376AB')
          doc.text('Spans:', m + 20, y)
          y += lh

          // span snippets
          doc.setFontSize(10).setTextColor('#000')
          const maxW = doc.internal.pageSize.getWidth() - (m + 60)
          const spanLines = doc.splitTextToSize(spansLine, maxW)
          doc.text(spanLines, m + 30, y)
          y += spanLines.length * lh + lh
        }
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