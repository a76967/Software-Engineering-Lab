<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title class="d-flex align-center">
        <span class="text-h5 font-weight-medium">Annotation Differences</span>
        <span class="subtitle-2 ms-4">Total Labels: {{ labelNames.length }}</span>
        <v-spacer />
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          placeholder="Search snippet"
          hide-details
          dense
          clearable
          style="max-width:300px"
        />
        <v-spacer />
        <v-btn text @click="goBack">Go Back</v-btn>
        <v-btn
          v-if="isAdmin"
          color="primary"
          dark
          @click="openThreshold"
        >
          Set Disagreement
        </v-btn>
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
          :sort-by="[]"
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.agreement="{ item }">
            <div class="d-flex justify-center">
              <div
                class="agreement-fill-circle"
                :style="{ borderColor: agreementColorDisplay(item) }"
              >
                <div
                  class="agreement-fill"
                  :style="{ height: item.agreement + '%', background:
                  agreementColorDisplay(item) }"
                ></div>
                <span class="agreement-label">{{ item.agreement }}%</span>
              </div>
            </div>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.conflict="{ item }">
            <span class="conflict-icon" :class="conflictClass(item)">
              {{ conflictSymbol(item) }}
            </span>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.snippet="{ item }">
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <span class="snippet-text" v-bind="attrs" v-on="on">
                  {{ item.snippet }}
                </span>
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

  data() {
    return {
      search: '',
      rows: [] as any[],
      headers: [] as any[],
      labelNames: [] as string[],
      threshold: 80,
      isLoading: false,
      error: '',
      decisionKey: '',
      isProjectAdmin: false
    }
  },

  computed: {
    filteredRows() {
      if (!this.search) return this.rows
      return this.rows.filter(r =>
        r.snippet.toLowerCase().includes(this.search.toLowerCase())
      )
    },
    isAdmin(): boolean {
      return this.isProjectAdmin
    }
  },

  mounted() {
    const stored = localStorage.getItem('disagreementThreshold')
    if (stored) {
      const v = parseInt(stored)
      if (!isNaN(v)) this.threshold = v
    }
    this.decisionKey = `disagreementDecisions:${this.$route.params.id}`
    this.fetchData()
  },

  async created() {
    const member = await this.$repositories.member.fetchMyRole(this.$route.params.id)
    this.isProjectAdmin = member.isProjectAdmin
  },

  methods: {
    goBack() {
      const pid = this.$route.params.id
      this.$router.push(`/projects/${pid}/disagreements`)
    },
    conflictClass(item: any) {
      if (item.decision === true) return 'red'
      if (item.decision === false) return 'green'
      const val = item.agreement
      return val >= this.threshold ? 'green' : val < this.threshold / 2 ? 'red' : 'orange'
    },
    conflictSymbol(item: any) {
      if (item.decision === true) return '✗'
      if (item.decision === false) return '✓'
      const val = item.agreement
      return val >= this.threshold ? '✓' : val < this.threshold / 2 ? '✗' : '⚠'
    },

    rowClass(item: any) {
      return item.decision === false || item.agreement < this.threshold / 2 ? 'low-agreement' : ''
    },
    agreementColor(val: number) {
      if (val >= this.threshold) return 'green'
      if (val >= this.threshold / 2) return 'orange'
      return 'red'
    },
    agreementColorDisplay(item: any) {
      if (item.decision === true) return 'red'
      if (item.decision === false) return 'green'
      return this.agreementColor(item.agreement)
    },

    async fetchData() {
      this.isLoading = true
      const pid = this.$route.params.id
      try {
        const { data } = await axios.get(`/v1/projects/${pid}/metrics/span-disagreements`)

        const labelSet = new Set<string>()
        data.forEach((r: any) => Object.keys(r.labels).forEach((l: string) => labelSet.add(l)))

        const labelList = Array.from(labelSet).sort()
        this.labelNames = labelList

        this.headers = [
          { text: 'Snippet', value: 'snippet', width: 250 },
          ...labelList.map(l => ({ text: l, value: l })),
          { text: 'Abstention', value: 'abstention', sortable: false },
          { text: 'X', value: 'x', sortable: false },
          { text: 'Agreement %', value: 'agreement', sortable: false },
          { text: 'State', value: 'conflict', sortable: false }
        ]

        this.rows = data.map((r: any) => {
          const row: Record<string, any> = {
            id: r.id,
            snippet: r.snippet,
            abstention: r.abstention || 0,
            x: r.x || 0,
            agreement: r.agreement,
            decision: null
          }
          labelSet.forEach(l => {
            row[l] = r.labels[l] || 0
          })
          return row
        })

        const raw = localStorage.getItem(this.decisionKey)
        if (raw) {
          try {
            const obj = JSON.parse(raw)
            this.rows.forEach(r => {
              if (Object.prototype.hasOwnProperty.call(obj, r.id)) {
                r.decision = obj[r.id]
              }
            })
          } catch (err) {
            console.error(err)
          }
        }

        // now count by conflict state and persist
        const greenCount = this.rows.filter(r => this.conflictClass(r) === 'green').length
        const total = this.rows.length
        const disagree = total - greenCount
        localStorage.setItem(`disagreementStats:${pid}`,
                             JSON.stringify({ total, disagree }))
      } catch (err: any) {
        console.error(err)
        this.error = "Error: Can't access our database!"
      } finally {
        this.isLoading = false
      }
    },

    openThreshold() {
      const pid = this.$route.params.id
      this.$router.push(`/projects/${pid}/disagreements/set`)
    },
    toDiscussion(r: any) {
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
  background-color: rgba(255, 0, 0, 0.1) !important;
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
.conflict-icon.green {
  color: #4caf50;
}
.conflict-icon.orange {
  color: #ff9800;
}
.conflict-icon.red {
  color: #f44336;
}

.agreement-fill-circle {
  position: relative;
  width: 36px;
  height: 36px;
  border: 2px solid;
  border-radius: 50%;
  overflow: hidden;
}
.agreement-fill {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
}
.agreement-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 10px;
  font-weight: 600;
}
</style>