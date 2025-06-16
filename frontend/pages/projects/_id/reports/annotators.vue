<template>
  <v-container fluid class="pa-4 d-flex flex-column" style="min-height: calc(100vh - 64px);">
    <div class="mt-12"></div>
    <h2 class="mt-4 mb-6">Annotators Report</h2>

    <!-- FILTROS -->
    <v-card elevation="2" class="mb-6">
      <v-card-title>Annotators Filters</v-card-title>
      <v-divider/>
      <v-card-text>
        <v-form @submit.prevent>
          <v-row dense>
            <!-- 2) Perspective -->
            <v-col cols="12" sm="4">
              <v-select
                v-model="filters.perspective"
                :items="perspectives"
                label="Perspective"
                clearable
              />
            </v-col>

            <!-- 3) Metrics -->
            <v-col cols="12" sm="4">
              <v-checkbox-group v-model="filters.metrics" row label="Metrics">
                <v-checkbox
                  v-for="m in metricsOptions"
                  :key="m.value"
                  :label="m.text"
                  :value="m.value"
                />
              </v-checkbox-group>
            </v-col>
          </v-row>

          <v-btn color="primary" @click="onClickReport">Generate Report</v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- TABELA DE RESULTADOS -->
    <v-card elevation="2" class="mt-6">
      <v-card-title>Results</v-card-title>
      <v-divider/>
      <v-card-text>
        <div v-if="loading" class="text-center my-6">
          <v-progress-circular indeterminate color="primary"/>
        </div>

        <v-data-table
          v-else-if="reportData.length"
          :headers="headers"
          :items="reportData"
          class="elevation-1"
          :items-per-page="10"
        />

        <div v-else class="text-center grey--text my-6">
          No data. Adjust filters and click “Generate Report.”
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import {
  VContainer, VCard, VCardTitle, VDivider, VCardText,
  VForm, VRow, VCol, VSelect,
  VCheckbox,
  VBtn, VDataTable, VProgressCircular
} from 'vuetify/lib'
import ApiService from '~/services/api.service'

export default Vue.extend({
  name: 'ReportsAnnotators',
  components: {
    VContainer, VCard, VCardTitle, VDivider, VCardText,
    VForm, VRow, VCol, VSelect,
    VCheckbox,
    VBtn, VDataTable, VProgressCircular
  },
  layout: 'workspace',
  data() {
    return {
      filters: {
        perspective: '',
        metrics: [] as string[]
      },
      perspectives: ['Country', 'Generation', 'Age'],
      metricsOptions: [
        { text: 'Total Annotations',        value: 'total' },
        { text: 'Agreement Rate',           value: 'agreement' },
        { text: 'Avg. Time per Annotation', value: 'avg_time' }
      ],
      reportData: [] as any[],
      loading: false,
      headers: [
        { text: 'Annotator', value: 'annotator' },
        { text: 'Total',      value: 'total',     align: 'end' },
        { text: 'Agreement %', value: 'agreement', align: 'end' },
        { text: 'Avg Time',   value: 'avg_time',  align: 'end' }
      ]
    }
  },

  methods: {
    onClickReport() {
      console.log('botão clicado, filtros =', this.filters)
      this.generateReport()
    },
    async generateReport() {
      this.loading = true
      try {
        const pid = this.$route.params.id
        // monta só os params que têm valor
        const params: any = {
          metrics: this.filters.metrics.join(',')
        }
        if (this.filters.perspective) {
          params.perspective = this.filters.perspective
        }

        const res = await ApiService.get(
          `/projects/${pid}/reports/annotators`,
          { params }
        )
        this.reportData = res.data.results || res.data
      } finally {
        this.loading = false
      }
    }
  }
})
</script>

<style scoped>
/* se precisar de ajustes visuais, adicione aqui */
</style>