<template>
  <v-card flat>
    <v-card-title class="d-flex align-center">
      <span class="headline mr-4">Annotation Differences</span>
      <v-spacer />
      <v-text-field
        v-model="search"
        dense
        hide-details
        append-icon="mdi-magnify"
        label="Search"
        style="max-width: 250px"
      />
    </v-card-title>
    <v-progress-circular v-if="isLoading" indeterminate color="primary" class="ma-4" />
    <v-alert v-if="error" type="error" dense class="ma-4">{{ error }}</v-alert>
    <v-data-table
      v-if="!isLoading && !error"
      :headers="headers"
      :items="filteredRows"
      dense
      disable-pagination
      hide-default-footer
      :item-class="rowClass"
    >
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.agreement="{ item }">
        <div class="d-flex justify-center align-center">
          <v-progress-circular
            :value="item.agreement"
            :size="34"
            :width="4"
            color="primary"
          >
            <small>{{ item.agreement }}%</small>
          </v-progress-circular>
        </div>
      </template>

      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.discussion="{ item }">
        <v-btn icon small @click="toDiscussion(item)">
          <v-icon>mdi-comment-outline</v-icon>
        </v-btn>
      </template>

      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.snippet="{ item }">
        <span style="max-width:180px; display:inline-block; white-space:nowrap;
        overflow:hidden; text-overflow:ellipsis;">{{ item.snippet }}</span>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'
import { VDataTable, VProgressCircular, VIcon, VBtn, VTextField, VAlert } from 'vuetify/lib'

interface Row { [key: string]: any }

export default Vue.extend({
  name: 'AnnotationDifferencesPage',
  components: { VDataTable, VProgressCircular, VIcon, VBtn, VTextField, VAlert },
  data () {
    return {
      search: '',
      rows: [] as Row[],
      headers: [] as any[],
      isLoading: false,
      error: ''
    }
  },
  computed: {
    filteredRows (): Row[] {
      if (!this.search) return this.rows
      return this.rows.filter(r => r.snippet.toLowerCase().includes(this.search.toLowerCase()))
    }
  },
  mounted () {
    this.fetchData()
  },
  methods: {
    rowClass (item: Row) {
      return item.agreement < 50 ? 'low-agreement' : ''
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
        const headers: any[] = [ { text: 'Snippet', value: 'snippet', width: '200' } ]
        const labelHeaders = Array.from(labelSet).sort().map(l => ({ text: l, value: l }))
        headers.push(...labelHeaders)
        headers.push({ text: 'Abstention', value: 'abstention', sortable: false })
        headers.push({ text: 'X', value: 'x', sortable: false })
        headers.push({ text: 'Total', value: 'total', sortable: false })
        headers.push({ text: 'Agreement', value: 'agreement', sortable: false })
        headers.push({ text: 'Discussion', value: 'discussion', sortable: false })
        this.headers = headers

        this.rows = data.map((r: any) => {
          const obj: Row = { id: r.id, snippet: r.snippet }
          labelSet.forEach(l => { obj[l] = r.labels[l] || 0 })
          obj.abstention = r.abstention || 0
          obj.x = r.x || 0
          obj.total = r.total
          obj.agreement = r.agreement
          return obj
        })
      } catch (err: any) {
        console.error('Error fetching data:', err.response || err.message)
        this.error = "Error: Can't access our database!"
      } finally {
        this.isLoading = false
      }
    },
    toDiscussion (r: Row) {
      const projectId = this.$route.params.id
      this.$router.push(`/projects/${projectId}/discussions/${r.id}`)
    }
  }
})
</script>

<style scoped>
tr.v-data-table__tr {
  transition: background 0.2s;
}
tr.low-agreement {
  background-color: rgba(255, 0, 0, 0.15) !important;
}
</style>