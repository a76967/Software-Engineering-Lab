<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title>
        <span class="text-h5 font-weight-medium">Annotation Differences</span>
        <v-spacer/>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          placeholder="Search snippet"
          hide-details
          dense
          clearable
          style="max-width:300px"
        />
        <v-btn text @click="openThreshold">Set Threshold</v-btn>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-data-table
          :headers="headers"
          :items="filteredRows"
          :loading="isLoading"
          dense
          disable-pagination
          hide-default-footer
          class="elevation-1"
          :item-class="rowClass"
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.agreement="{ item }">
            <div class="d-flex justify-center">
              <v-progress-circular
                :value="item.agreement"
                :size="36"
                :width="4"
                :color="agreementColor(item.agreement)"
              >
                <small>{{ item.agreement }}%</small>
              </v-progress-circular>
            </div>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.conflict="{ item }">
            <span
              class="conflict-icon"
              :class="conflictClass(item.agreement)"
            >
              {{ conflictSymbol(item.agreement) }}
            </span>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.snippet="{ item }">
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <span
                  class="snippet-text"
                  v-bind="attrs"
                  v-on="on"
                >{{ item.snippet }}</span>
              </template>
              <span>{{ item.snippet }}</span>
            </v-tooltip>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
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
      rows: [] as any[],
      headers: [] as any[],
      threshold: 80,
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
    const stored = localStorage.getItem('disagreementThreshold')
    if (stored) {
      const v = parseInt(stored)
      if (!isNaN(v)) this.threshold = v
    }
    this.fetchData()
  },

  methods: {
    conflictClass(val:number) {
      return val >= this.threshold ? 'green'
           : val <  this.threshold/2 ? 'red'
           : 'orange'
    },
    conflictSymbol(val:number) {
      return val >= this.threshold ? '✓'
           : val <  this.threshold/2 ? '✗'
           : '⚠'
    },

    rowClass (item:any) {
      return item.agreement < this.threshold / 2 ? 'low-agreement' : ''
    },
    agreementColor (val:number) {
      if (val >= this.threshold)         return 'green'
      if (val >= this.threshold / 2)     return 'orange'
      return 'red'
    },

    async fetchData () {
      this.isLoading = true
      const pid = this.$route.params.id
      try {
        const { data } = await axios.get(
          `/v1/projects/${pid}/metrics/span-disagreements`
        )

        const labelSet = new Set<string>()
        data.forEach((r:any) =>
          Object.keys(r.labels).forEach((l:string) => labelSet.add(l))
        )

        this.headers = [
          { text:'Snippet', value:'snippet', width:250 },
          ...Array.from(labelSet).sort().map(l => ({ text:l, value:l })),
          { text:'Abstention', value:'abstention', sortable:false },
          { text:'X',          value:'x',          sortable:false },
          { text:'Assignees',  value:'total',      sortable:false },
          { text:'Agreement',  value:'agreement',  sortable:false },
          { text:'Conflict?',  value:'conflict',   sortable:false }
        ]

        this.rows = data.map((r:any) => {
          const row:Record<string,any> = {
            id:        r.id,
            snippet:   r.snippet,
            abstention:r.abstention||0,
            x:         r.x||0,
            total:     r.total,
            agreement: r.agreement
          }
          labelSet.forEach(l => { row[l] = r.labels[l] || 0 })
          return row
        })
      } catch(err:any) {
        console.error(err)
        this.error = "Error: Can't access our database!"
      } finally {
        this.isLoading = false
      }
    },

    openThreshold () {
      const pid = this.$route.params.id
      this.$router.push(`/projects/${pid}/disagreements/threshold`)
    },
    toDiscussion (r:any) {
      const pid = this.$route.params.id
      this.$router.push(`/projects/${pid}/discussions/${r.id}`)
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
  height: 64px !important;
  background-color: white !important;
}

.low-agreement {
  background-color: rgba(255,0,0,0.1) !important;
}

.conflict-icon {
  font-weight: 700;
  font-size: 1.3rem;
  line-height: 1;
  display: inline;
  padding: 0;
  background: transparent !important;
  border: none !important;
  transition: color 0.3s ease;
}
.conflict-icon.green  { color: #4caf50; }
.conflict-icon.orange { color: #ff9800; }
.conflict-icon.red    { color: #f44336; }

</style>