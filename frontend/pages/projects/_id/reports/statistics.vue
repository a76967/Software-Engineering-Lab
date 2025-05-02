<template>
    <v-container
      fluid
      class="pa-4 d-flex flex-column"
      style="min-height: calc(100vh - 64px);"
    >
      <div class="mt-12"></div>

      <h2 class="mt-4 mb-6">Annotation Statistics</h2>
  
      <v-card elevation="2" class="mb-6">
        <v-card-title>Statistics Filters</v-card-title>
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
                      label="Date Range"
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
                  label="Annotator Perspective"
                  clearable
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="filters.itemType"
                  :items="itemTypes"
                  label="Item Type"
                  clearable
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-radio-group
                  v-model="filters.chartType"
                  row
                  label="Chart Type"
                >
                  <v-radio label="Pie chart" value="pie"/>
                  <v-radio label="Histogram" value="histogram"/>
                </v-radio-group>
              </v-col>
            </v-row>

            <v-row>
              <v-spacer/>
              <v-btn color="primary" type="submit">
                Generate Statistics
              </v-btn>
            </v-row>
          </v-form>
        </v-card-text>
      </v-card>
  
      <v-card elevation="2">
        <v-card-title>Results</v-card-title>
        <v-divider/>
        <v-card-text>
          <div v-if="loading" class="text-center my-6">
            <v-progress-circular indeterminate color="primary"/>
          </div>
          <div v-else-if="statsData.length">
            <div v-if="filters.chartType === 'pie'">
              <p>Pie chart would render here.</p>
            </div>
            <div v-else>
              <p>Histogram would render here.</p>
            </div>
          </div>
          <div v-else class="text-center grey--text my-6">
            No data. Adjust filters and click “Generate Statistics.”
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
    VSelect, VRadioGroup, VRadio, VBtn, VSpacer,
    VProgressCircular
  } from 'vuetify/lib'
  import ApiService from '~/services/api.service'
  
  export default Vue.extend({
    name: 'ReportsStatistics',
    components: {
      VContainer, VCard, VCardTitle, VDivider, VCardText,
      VForm, VRow, VCol, VMenu, VDatePicker, VTextField,
      VSelect, VRadioGroup, VRadio, VBtn, VSpacer,
      VProgressCircular
    },
    layout: 'workspace',
    data() {
      return {
        loading: false,
        filters: {
          dateRange: { start: '', end: '' },
          dateRangeText: '',
          perspective: '',
          itemType: '',
          chartType: 'pie'
        },
        dateMenu: false,
        perspectives: ['Country', 'Generation', 'Age Group'],
        itemTypes: ['Category A', 'Category B', 'Category C'],
        statsData: [] as any[]
      }
    },
    methods: {
      updateDateText() {
        const { start, end } = this.filters.dateRange
        this.filters.dateRangeText = start && end
          ? `${start} → ${end}` : ''
      },
      async generateReport() {
        this.loading = true
        try {
          const params = {
            date_start: this.filters.dateRange.start,
            date_end: this.filters.dateRange.end,
            perspective: this.filters.perspective,
            item_type: this.filters.itemType
          }
          const res = await ApiService.get(
            `/projects/${this.$route.params.id}/reports/statistics`,
            { params }
          )
          this.statsData = res.data
        } catch (e) {
          console.error('Failed to fetch statistics:', e)
          this.statsData = []
        } finally {
          this.loading = false
        }
      }
    }
  })
  </script>
  
  <style scoped>
  
  </style>