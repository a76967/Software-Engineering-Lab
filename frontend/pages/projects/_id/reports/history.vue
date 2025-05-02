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
                <v-autocomplete
                  v-model="filters.user"
                  :items="users"
                  item-text="name"
                  item-value="id"
                  label="Annotator"
                  clearable
                />
              </v-col>
  
              <v-col cols="12" sm="6">
                <v-autocomplete
                  v-model="filters.annotators"
                  :items="users"
                  item-text="name"
                  item-value="id"
                  label="Specific Annotators"
                  multiple
                  clearable
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
              <v-btn color="primary" type="submit">
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
          <div v-if="loading" class="text-center my-6">
            <v-progress-circular indeterminate color="primary"/>
          </div>
          <v-data-table
            v-else-if="historyData.length"
            :headers="headers"
            :items="historyData"
            class="elevation-1"
            :items-per-page="10"
          />
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
    VForm, VRow, VCol, VMenu, VDatePicker, VTextField,
    VAutocomplete, VSelect, VBtn, VSpacer,
    VDataTable, VProgressCircular
  } from 'vuetify/lib'
  import ApiService from '~/services/api.service'
  
  export default Vue.extend({
    name: 'ReportsHistory',
    components: {
      VContainer, VCard, VCardTitle, VDivider, VCardText,
      VForm, VRow, VCol, VMenu, VDatePicker, VTextField,
      VAutocomplete, VSelect, VBtn, VSpacer,
      VDataTable, VProgressCircular
    },
    layout: 'workspace',
    data() {
      return {
        loading: false,
        filters: {
          dateRange: { start: '', end: '' },
          dateRangeText: '',
          user: null as number|null,
          annotators: [] as number[],
          perspective: '',
          resolution: ''
        },
        dateMenu: false,
        users: [] as Array<{ id: number; name: string }>,
        perspectives: ['Portugal', 'Generation X', 'Generation Y', 'Generation Z'],
        resolutionStates: ['Before Rules', 'After Rules'],
        historyData: [] as any[],
        headers: [
          { text: 'Timestamp', value: 'timestamp' },
          { text: 'Annotator', value: 'user' },
          { text: 'Action', value: 'action' },
          { text: 'Details', value: 'details' }
        ]
      }
    },
    async mounted() {
      const res = await ApiService.get(`/projects/${this.$route.params.id}/members`)
      this.users = res.data
    },
    methods: {
      updateDateText() {
        const { start, end } = this.filters.dateRange
        this.filters.dateRangeText = start && end ? `${start} → ${end}` : ''
      },
      async generateReport() {
        this.loading = true
        try {
          const params: any = {
            date_start: this.filters.dateRange.start,
            date_end: this.filters.dateRange.end,
            user: this.filters.user,
            annotators: this.filters.annotators,
            perspective: this.filters.perspective,
            resolution: this.filters.resolution
          }
          const res = await ApiService.get(
            `/projects/${this.$route.params.id}/reports/history`,
            { params }
          )
          this.historyData = res.data
        } catch {
          this.historyData = []
        } finally {
          this.loading = false
        }
      }
    }
  })
  </script>
  
  <style scoped>
  
  </style>