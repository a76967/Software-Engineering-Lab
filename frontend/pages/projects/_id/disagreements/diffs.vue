<template>
  <v-card flat class="pa-4">
    <v-card-title class="d-flex align-center mb-4">
      <span class="text-h5 font-weight-medium mr-4">Annotation Differences</span>
      <v-spacer />
      <v-text-field
        v-model="search"
        dense
        outlined
        hide-details
        append-icon="mdi-magnify"
        label="Search snippet"
        class="search-bar"
        style="max-width: 300px"
      />
    </v-card-title>

    <v-progress-circular
      v-if="isLoading"
      indeterminate
      color="primary"
      class="my-6 mx-auto d-block"
      size="40"
      width="5"
    />
    <v-alert
      v-if="error"
      type="error"
      border="left"
      elevation="2"
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <v-data-table
      v-if="!isLoading && !error"
      :headers="headers"
      :items="filteredRows"
      dense
      disable-pagination
      hide-default-footer
      class="elevation-1"
      :item-class="rowClass"
    >
    
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.agreement="{ item }">
        <div class="d-flex justify-center align-center">
          <v-progress-circular
            :value="item.agreement"
            :size="36"
            :width="4"
            :color="agreementColor(item.agreement)"
          >
            <small class="text-caption font-weight-medium">{{ item.agreement }}%</small>
          </v-progress-circular>
        </div>
      </template>

      
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.discussion="{ item }">
        <v-tooltip bottom>
          <template #activator="{ on, attrs }">
            <v-btn icon small @click="toDiscussion(item)" v-bind="attrs" v-on="on">
              <v-icon>mdi-comment-outline</v-icon>
            </v-btn>
          </template>
          <span>Go to discussion</span>
        </v-tooltip>
      </template>

      
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.snippet="{ item }">
        <v-tooltip bottom>
          <template #activator="{ on, attrs }">
            <span
              class="snippet-text"
              v-bind="attrs"
              v-on="on"
            >
              {{ item.snippet }}
            </span>
          </template>
          <span>{{ item.snippet }}</span>
        </v-tooltip>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'

export default Vue.extend({
  name: 'AnnotationDifferencesPage',
  layout: 'project',
  data () {
    return {
      search: '',
      rows: [],
      headers: [],
      isLoading: false,
      error: ''
    }
  },
  computed: {
    filteredRows () {
      if (!this.search) return this.rows
      return this.rows.filter(r =>
        r.snippet.toLowerCase().includes(this.search.toLowerCase())
      )
    }
  },
  mounted () {
    this.fetchData()
  },
  methods: {
    rowClass (item) {
      return item.agreement < 50 ? 'low-agreement' : ''
    },
    agreementColor (value: number): string {
      if (value >= 75) return 'green'
      if (value >= 50) return 'orange'
      return 'red'
    },
    async fetchData () {
      this.isLoading = true
      const projectId = this.$route.params.id
      try {
        const { data } = await axios.get(`/v1/projects/${projectId}/metrics/span-disagreements`)
        const labelSet = new Set<string>()
        data.forEach((row: any) => {
          Object.keys(row.labels).forEach((l: string) => labelSet.add(l))
        })

        const headers = [
          { text: 'Snippet',     value: 'snippet',    width: '250' },
          ...Array.from(labelSet).sort().map(l => ({ text: l, value: l })),
          { text: 'Abstention',  value: 'abstention', sortable: false },
          { text: 'X',           value: 'x',          sortable: false },
          { text: 'Asignees',       value: 'total',      sortable: false },
          { text: 'Agreement',   value: 'agreement',  sortable: false },
          { text: 'Discussion',  value: 'discussion', sortable: false }
        ]
        this.headers = headers

        this.rows = data.map((r: any) => {
          const row: Record<string, any> = {
            id:       r.id,
            snippet:  r.snippet
          }
          labelSet.forEach(l => {
            row[l] = r.labels[l] || 0
          })
          row.abstention = r.abstention || 0
          row.x          = r.x || 0
          row.total      = r.total
          row.agreement  = r.agreement
          return row
        })
      } catch (err: any) {
        console.error('Error fetching data:', err.response || err.message)
        this.error = "Error: Can't access our database!"
      } finally {
        this.isLoading = false
      }
    },
    toDiscussion (r) {
      const projectId = this.$route.params.id
      this.$router.push(`/projects/${projectId}/discussions/${r.id}`)
    }
  }
})
</script>

<style scoped>
.snippet-text {
  max-width: 220px;
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
tr.v-data-table__tr {
  transition: background-color 0.2s;
}
tr.low-agreement {
  background-color: rgba(255, 0, 0, 0.1) !important;
}
</style>