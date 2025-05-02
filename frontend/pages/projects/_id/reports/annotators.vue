<template>
    <v-container
      fluid
        class="pa-4 d-flex flex-column"
        style="min-height: calc(100vh - 64px);"
    >
      <div class="mt-12"></div>
      <h2 class="mt-4 mb-6">Annotators Report</h2>
  
      <v-card elevation="2" class="mb-6">
        <v-card-title>Annotators Filters</v-card-title>
        <v-divider/>
        <v-card-text>
          <v-form @submit.prevent="generateReport">
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-menu
                  v-model="dateMenu"
                  :close-on-content-click="false"
                  offset-y
                >
                  <template #activator="{ on, attrs }">
                    <v-text-field
                      v-model="filters.dateRangeText"
                      label="Analysis Period"
                      readonly
                      clearable
                      v-bind="attrs"
                      v-on="on"
                    />
                  </template>
                  <v-date-picker
                    v-model="filters.dateRange"
                    range
                    scrollable
                    @change="updateDateText"
                  />
                </v-menu>
              </v-col>
  
              <v-col cols="12" sm="6">
                <v-select
                  v-model="filters.perspective"
                  :items="perspectives"
                  label="Perspective"
                  clearable
                />
              </v-col>
  
              <v-col cols="12">
                <v-checkbox-group
                  v-model="filters.metrics"
                  row
                  label="Select Metrics"
                >
                  <v-checkbox
                    v-for="m in metricsOptions"
                    :key="m.value"
                    :label="m.text"
                    :value="m.value"
                  />
                </v-checkbox-group>
              </v-col>
            </v-row>
  
            <v-row>
              <v-spacer/>
              <v-btn color="primary" type="submit">
                Generate Report
              </v-btn>
            </v-row>
          </v-form>
        </v-card-text>
      </v-card>
  
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
    VForm, VRow, VCol, VMenu, VDatePicker, VTextField,
    VSelect, VCheckbox, VBtn,
    VSpacer, VDataTable, VProgressCircular
  } from 'vuetify/lib'
  import ApiService from '~/services/api.service'
  
  export default Vue.extend({
    name: 'ReportsAnnotators',
    components: {
      VContainer, VCard, VCardTitle, VDivider, VCardText,
      VForm, VRow, VCol, VMenu, VDatePicker, VTextField,
      VSelect, VCheckbox, VBtn,
      VSpacer, VDataTable, VProgressCircular
    },
    layout: 'workspace',
    data() {
      return {
        loading: false,
        filters: {
          dateRange: { start: '', end: '' },
          dateRangeText: '',
          perspective: '',
          metrics: [] as string[]
        },
        dateMenu: false,
        perspectives: ['Country', 'Generation', 'Age'],
        metricsOptions: [
          { text: 'Total Annotations', value: 'total' },
          { text: 'Agreement Rate', value: 'agreement' },
          { text: 'Avg. Time per Annotation', value: 'avg_time' }
        ],
        reportData: [] as any[],
        headers: [
          { text: 'Annotator', value: 'annotator' },
          { text: 'Total', value: 'total' },
          { text: 'Agreement %', value: 'agreement' },
          { text: 'Avg Time', value: 'avg_time' }
        ]
      }
    },
    methods: {
      updateDateText() {
        const { start, end } = this.filters.dateRange
        this.filters.dateRangeText = start && end
          ? `${start} → ${end}`
          : ''
      },
      async generateReport() {
        this.loading = true
        try {
          const params = {
            ...this.filters,
            date_start: this.filters.dateRange.start,
            date_end: this.filters.dateRange.end
          }
          const res = await ApiService.get(
            `/projects/${this.$route.params.id}/reports/annotators`,
            { params }
          )
          this.reportData = res.data
        } catch (e) {
          console.error(e)
          this.reportData = []
        } finally {
          this.loading = false
        }
      }
    }
  })
  </script>
  
  <style scoped>
  
  </style>