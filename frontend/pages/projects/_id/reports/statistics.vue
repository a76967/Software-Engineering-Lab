<template>
  <v-container
    fluid
    class="pa-4 d-flex flex-column"
    style="min-height: calc(100vh - 64px);"
  >
    <div class="mt-12"></div>
    <h2 class="mt-4 mb-6">Annotations Statistics</h2>

    <v-card elevation="2" class="mb-6">
      <v-card-title>Filters</v-card-title>
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
                no-data-text="No annotators"
                loading-text="Loading…"
              />
            </v-col>

            <v-col cols="12" sm="6">
              <v-radio-group v-model="filters.chartType" row label="Chart Type">
                <v-radio label="Bar" value="bar"/>
                <v-radio label="Pie" value="pie"/>
              </v-radio-group>
            </v-col>
          </v-row>

          <v-row>
            <v-spacer/>
            <v-btn color="primary" type="submit" :disabled="!filters.annotators.length">
              Generate
            </v-btn>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <v-slide-y-transition mode="out-in">
      <v-card key="results" elevation="2">
        <v-card-title>Results</v-card-title>
        <v-divider/>
        <v-card-text>
          <div v-if="loading" class="text-center my-6">
            <v-progress-circular indeterminate color="primary"/>
          </div>

          <div v-else-if="statsData.length">
            <div class="legend-tags">
              <span
                v-for="(label, idx) in chartData.labels"
                :key="label"
                class="legend-tag"
              >
                <span
                  class="legend-color"
                  :style="{ backgroundColor: chartData.datasets[0].backgroundColor[idx] }"
                />
                {{ label }}
              </span>
            </div>

            <div class="chart-wrapper">
              <bar-chart
                v-if="filters.chartType==='bar'"
                ref="chartRef"
                :chart-data="chartData"
                :options="chartOptions"
              />
              <pie-chart
                v-else
                ref="chartRef"
                :chart-data="chartData"
                :options="chartOptions"
              />
            </div>

            <v-btn class="mt-4" color="primary" @click="downloadPdf">
              Download PDF
            </v-btn>
          </div>

          <div v-else class="text-center grey--text my-6">
            No data. Adjust filters and click “Generate.”
          </div>
        </v-card-text>
      </v-card>
    </v-slide-y-transition>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import type { PropType } from 'vue'
import {
  VContainer, VCard, VCardTitle, VDivider, VCardText,
  VForm, VRow, VCol, VAutocomplete, VBtn, VSpacer,
  VRadioGroup, VRadio, VProgressCircular, VSlideYTransition
} from 'vuetify/lib'
import { Bar, Pie, mixins } from 'vue-chartjs'
import { jsPDF as JsPDF } from 'jspdf'
import ApiService from '~/services/api.service'
const { reactiveProp } = mixins

export default Vue.extend({
  name: 'ReportsStatistics',
  components: {
    VContainer, VCard, VCardTitle, VDivider, VCardText,
    VForm, VRow, VCol, VAutocomplete, VBtn, VSpacer,
    VRadioGroup, VRadio, VProgressCircular, VSlideYTransition,
    BarChart: {
      extends: Bar,
      mixins: [reactiveProp],
      props: {
        chartData: { type: Object as PropType<any>, required: true },
        chartOptions: { type: Object as PropType<any>, required: true }
      },
      mounted() {
        ;(this as any).renderChart(this.chartData, this.chartOptions)
      }
    },
    PieChart: {
      extends: Pie,
      mixins: [reactiveProp],
      props: {
        chartData: { type: Object as PropType<any>, required: true },
        chartOptions: { type: Object as PropType<any>, required: true }
      },
      mounted() {
        ;(this as any).renderChart(this.chartData, this.chartOptions)
      }
    }
  },
  layout: 'workspace',

  data() {
    return {
      loading: false,
      filters: {
        annotators: [] as number[],
        chartType: 'bar'
      },
      users: [] as Array<{ id: number; name: string }>,
      allAnnotationsRaw: [] as any[],
      statsData: [] as { id: number; category: string; count: number }[],

      chartData: {
        labels: [] as string[],
        datasets: [{
          data: [] as number[],
          backgroundColor: [] as string[]
        }]
      },
      userColors: {} as Record<number, string>,
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: 0 },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              callback: (value: any) => `${value}`
            },
            max: undefined as number | undefined
          }
        },
        plugins: {
          legend: {
            display: false,   // ← força remover qualquer legenda
            labels: { filter: () => false } // opcional: filtra tudo
          },
          tooltip: { enabled: true }
        }
      }
    }
  },

  computed: {
    annotatorOptions(): Array<{ id: number; name: string }> {
      const used = new Set(this.allAnnotationsRaw.map(a => a.annotator))
      return this.users.filter(u => used.has(u.id))
    },
    sortedStats(): Array<{ category: string; count: number }> {
      return [...this.statsData].sort((a,b) => b.count - a.count)
    }
  },

  async mounted() {
    const pid = Number(this.$route.params.id)
    try {
      const res = await ApiService.get('/annotations/', { params: { project: pid } })
      const raw = res.data.results || res.data
      this.allAnnotationsRaw = raw.map((a: any) => ({
        ...a,
        annotator: Number(typeof a.annotator === 'object' ? a.annotator.id : a.annotator)
      }))
    } catch {
      this.allAnnotationsRaw = []
    }
    try {
      const u = await ApiService.get('/users/')
      const list = u.data.results || u.data
      this.users = list.map((x: any) => ({
        id: x.id,
        name: x.username || x.name || `${x.first_name || ''} ${x.last_name || ''}`.trim()
      }))
    } catch {
      this.users = []
    }
  },

  methods: {
    getColor(id: number): string {
      if (!this.userColors[id]) {
        this.userColors[id] = this.randomColor()
      }
      return this.userColors[id]
    },
    randomColor(): string {
      const r = Math.floor(Math.random() * 156 + 100)
      const g = Math.floor(Math.random() * 156 + 100)
      const b = Math.floor(Math.random() * 156 + 100)
      return `rgb(${r},${g},${b})`
    },

    generateReport() {
      this.loading = true
      const chosen = this.filters.annotators.length
        ? this.filters.annotators
        : this.annotatorOptions.map(u => u.id)

      const counts: Record<number, number> = {}
      this.allAnnotationsRaw.forEach(a => {
        if (chosen.includes(a.annotator)) {
          counts[a.annotator] = (counts[a.annotator] || 0) + 1
        }
      })

      const data = Object.entries(counts).map(([uid, c]) => {
        const id = +uid
        return {
          id,
          category: this.users.find(u => u.id === id)?.name || uid,
          count: c
        }
      })
      this.statsData = data

      const maxCount = Math.max(...data.map(r => r.count), 0)
      ;(this.chartOptions.scales.y as any).max = maxCount + 3

      this.chartData = {
        labels: data.map(r => r.category),
        datasets: [{
          data: data.map(r => r.count),
          backgroundColor: data.map(r => this.getColor(r.id))
        }]
      }

      this.loading = false
    },

    downloadPdf() {
      const doc = new JsPDF({ unit: 'pt', format: 'letter' })
      const pageW = doc.internal.pageSize.getWidth()
      const margin = 40
      let y = margin
      const lineH = 14

      doc.setFontSize(18).text('Annotations Statistics', margin, y)
      y += lineH * 2

      const chartComp = this.$refs.chartRef as any
      const canvas: HTMLCanvasElement = chartComp.$el.querySelector('canvas')
      const imgData = canvas.toDataURL('image/png')
      const imgWidth = (pageW - margin * 2) * 0.5
      const imgHeight = (canvas.height / canvas.width) * imgWidth
      const x = (pageW - imgWidth) / 2
      doc.addImage(imgData, 'PNG', x, y, imgWidth, imgHeight)
      y += imgHeight + lineH * 1.5

      doc.setFontSize(12)
      this.statsData.forEach(r => {
        if (y + lineH > doc.internal.pageSize.getHeight() - margin) {
          doc.addPage()
          y = margin
        }
        doc.text(`${r.category}: ${r.count}`, margin, y)
        y += lineH
      })

      doc.save('annotations-statistics.pdf')
    }
  }
})
</script>

<style scoped>
.v-slide-y-transition-enter-active,
.v-slide-y-transition-leave-active {
  transition: all .3s ease;
}
.v-slide-y-transition-enter,
.v-slide-y-transition-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.chart-wrapper {
  width: 300px;
  height: 300px;
  margin: 0 auto 16px;
  position: relative;
}

.chart-wrapper canvas {
  width: 100% !important;
  height: 100% !important;
}

.legend-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  justify-content: center;
}
.legend-tag {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #f0f0f0;
  border-radius: 16px;
  font-size: 0.875rem;
  color: #333;
}
.legend-color {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 6px;
}
</style>