<template>
  <v-container
    fluid
    class="pa-4 d-flex flex-column"
    style="min-height: calc(100vh - 64px);"
  >
    <div class="mt-12"></div>

    <h2 class="mt-4  mb-6">Annotations Report</h2>

    <v-card elevation="2" class="mb-6">
      <v-card-title>Annotation Filters</v-card-title>
      <v-divider/>
      <v-card-text>
        <v-form @submit.prevent="generateReport">
          <v-row dense>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="filters.item"
                label="Item ID or Text"
                clearable
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-autocomplete
                v-model="filters.annotator"
                :items="annotators"
                item-text="name"
                item-value="id"
                label="Annotator"
                clearable
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="filters.label"
                :items="labels"
                label="Assigned Label"
                clearable
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
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
      <v-card-title>
        <span class="subtitle-1">Results</span>
        <v-spacer/>
        <v-btn
          icon
          :disabled="!tableData.length"
          @click="exportCsv"
        >
          <v-icon>mdi-file-delimited</v-icon>
        </v-btn>
        <v-btn
          icon
          class="ml-2"
          :disabled="!tableData.length"
          @click="exportPdf"
        >
          <v-icon>mdi-file-pdf</v-icon>
        </v-btn>
      </v-card-title>
      <v-divider/>
      <v-card-text>
        <div v-if="loading" class="text-center my-6">
          <v-progress-circular indeterminate color="primary"/>
        </div>

        <v-data-table
          v-else-if="tableData.length"
          :headers="headers"
          :items="tableData"
          :search="search"
          class="elevation-1"
          :items-per-page="10"
        >
          <template #top>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
            />
          </template>
          <template #[`item.timestamp`]="{ item }">
            {{ formatDate(item.timestamp) }}
          </template>
        </v-data-table>

        <div v-else class="text-center grey--text my-6">
          No results. Adjust filters and click “Generate Report.”
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import {
  VContainer, VForm, VRow, VCol, VTextField,
  VSelect, VMenu, VDatePicker, VBtn, VDataTable,
  VDivider, VCard, VCardTitle, VCardText
} from 'vuetify/lib'
import ApiService from '~/services/api.service'

export default Vue.extend({
  layout: 'workspace',
  name: 'ReportsAnnotations',
  components: 
  { VContainer, VForm, VRow, VCol, VTextField, 
    VSelect, VMenu, VDatePicker, VBtn, VDataTable, 
    VDivider, VCard, VCardTitle, VCardText },
  data() {
    return {
      loading: false,
      filters: {
        item: '',
        annotator: null as number|null,
        label: '',
        dateRange: { start: '', end: '' },
        dateRangeText: ''
      },
      dateMenu: false,
      annotators: [] as Array<{ id: number; name: string }>,
      labels: [] as string[],
      tableData: [] as any[],
      headers: [
        { text: 'Item', value: 'item' },
        { text: 'Annotator', value: 'annotator' },
        { text: 'Label', value: 'label' },
        { text: 'Perspective', value: 'perspective' },
        { text: 'Timestamp', value: 'timestamp' }
      ],
      search: ''
    }
  },
  async mounted() {
    try {
      const [membersRes, labelsRes] = await Promise.all([
        ApiService.get(`/projects/${this.$route.params.id}/members`),
        ApiService.get(`/projects/${this.$route.params.id}/labels`)
      ])
      this.annotators = membersRes.data
      this.labels     = labelsRes.data
    } catch (err) {
      console.error('Failed to load annotators or labels:', err)
      this.annotators = []
      this.labels     = []
    }
  },
  methods: {
    updateDateText() {
      const { start, end } = this.filters.dateRange
      this.filters.dateRangeText = start && end ? `${start} → ${end}` : ''
    },
    async generateReport() {
      this.loading = true
      const params: any = { ...this.filters }
      delete params.dateMenu
      delete params.dateRangeText
      const res = await ApiService.get(
        `/projects/${this.$route.params.id}/reports/annotations`,
        { params }
      )
      this.tableData = res.data
      this.loading = false
    },
    formatDate(ts: string) {
      return new Date(ts).toLocaleString()
    },
    exportCsv() {
    
    },
    exportPdf() {

    }
  }
})
</script>

<style scoped>

</style>