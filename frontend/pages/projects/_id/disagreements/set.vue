<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title class="d-flex align-center">
        <span class="text-h5 font-weight-medium">Set Disagreement</span>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="rows"
        :loading="isLoading"
        dense
        disable-pagination
        hide-default-footer
        class="elevation-1"
        :item-class="rowClass"
      >
        <!-- Agreement column (unchanged visual) -->
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

        <!-- Conflict column: click to toggle Yes (✓) / No (✗) decision -->
        <!-- eslint-disable-next-line vue/valid-v-slot -->
        <template #item.conflict="{ item }">
          <v-btn icon small @click.stop="toggleDecision(item)" class="pa-0 ma-0">
            <span class="conflict-icon" :class="conflictClass(item)">
              {{ conflictSymbol(item) }}
            </span>
          </v-btn>
        </template>

        <!-- Snippet column -->
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

      <v-card-actions>
        <v-spacer />
        <v-btn text @click="onCancel">Cancel</v-btn>

        <v-btn
          :disabled="localThreshold === initialThreshold"
          text
          @click="onRestore"
        >
          Restore Previous ({{ initialThreshold }}%)
        </v-btn>

        <v-btn
          :disabled="localThreshold === initialThreshold"
          color="primary"
          @click="openConfirm"
        >
          Save
        </v-btn>
      </v-card-actions>

      <!-- Confirm dialog -->
      <v-dialog v-model="confirmDialog" max-width="400">
        <v-card>
          <v-card-title class="headline">Confirm Threshold Change</v-card-title>
          <v-card-text>
            Change threshold from
            <strong>{{ initialThreshold }}%</strong>
            to
            <strong>{{ localThreshold }}%</strong>?
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="confirmDialog = false">No</v-btn>
            <v-btn color="primary" @click="onConfirm">Yes</v-btn>
          </v-btn>
        </v-card>
      </v-dialog>

      <!-- Toast -->
      <v-snackbar v-model="snackbar" top right timeout="2000">
        Threshold updated to {{ localThreshold }}%!
      </v-snackbar>
    </v-card>
  </v-container>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'

export default Vue.extend({
  name: 'DisagreementThresholdPage',
  layout: 'project',

  data() {
    const storedThresh = localStorage.getItem('disagreementThreshold')
    const initThresh = storedThresh ? parseInt(storedThresh, 10) : 80

    return {
      initialThreshold: isNaN(initThresh) ? 80 : initThresh,
      localThreshold: isNaN(initThresh) ? 80 : initThresh,
      rows: [] as any[],
      headers: [] as any[],
      isLoading: false,
      error: '',
      confirmDialog: false,
      snackbar: false
    }
  },

  watch: {
    localThreshold(val: number) {
      const num = Math.max(0, Math.min(100, Number(val) || 0))
      if (num !== val) {
        this.$nextTick(() => {
          this.localThreshold = num
        })
        return
      }
      // Re-evaluate row colors when threshold changes
      this.rows = [...this.rows]
    }
  },

  mounted() {
    this.fetchData()
  },

  methods: {
    /**
     * Toggle decision for a given row.
     * true  => ✓ (green)
     * false => ✗ (red)
     * null  => fallback to automatic (orange/green/red based on %)
     */
    toggleDecision(row: any) {
      if (row.decision === null || row.decision === undefined) {
        // First click => mark as YES (✓)
        row.decision = true
      } else if (row.decision === true) {
        // Second click => mark as NO (✗)
        row.decision = false
      } else {
        // Third click => reset to automatic
        row.decision = null
      }
      this.saveDecisions()
    },

    saveDecisions() {
      const map: Record<string, boolean> = {}
      this.rows.forEach(r => {
        if (r.decision !== null && r.decision !== undefined) {
          map[r.id] = r.decision
        }
      })
      localStorage.setItem('disagreementDecisions', JSON.stringify(map))
    },

    loadDecisions() {
      try {
        const data = JSON.parse(localStorage.getItem('disagreementDecisions') || '{}')
        this.rows.forEach(r => {
          if (data.hasOwnProperty(r.id)) {
            r.decision = data[r.id]
          }
        })
      } catch (e) {
        // Ignore malformed JSON
      }
    },

    conflictClass(item: any) {
      if (item.decision === true) return 'green'
      if (item.decision === false) return 'red'

      // Automatic coloring based on threshold
      const val = item.agreement
      return val >= this.localThreshold ? 'green' : val < this.localThreshold / 2 ? 'red' : 'orange'
    },

    conflictSymbol(item: any) {
      if (item.decision === true) return '✓'
      if (item.decision === false) return '✗'

      const val = item.agreement
      return val >= this.localThreshold ? '✓' : val < this.localThreshold / 2 ? '✗' : '⚠'
    },

    rowClass(item: any) {
      return item.decision === false || item.agreement < this.localThreshold / 2 ? 'low-agreement' : ''
    },

    agreementColor(val: number) {
      if (val >= this.localThreshold) return 'green'
      if (val >= this.localThreshold / 2) return 'orange'
      return 'red'
    },

    async fetchData() {
      this.isLoading = true
      const pid = Number(this.$route.params.id)
      try {
        const { data } = await axios.get(`/v1/projects/${pid}/metrics/span-disagreements`)

        const labelSet = new Set<string>()
        data.forEach((r: any) => Object.keys(r.labels).forEach(l => labelSet.add(l)))

        this.headers = [
          { text: 'Snippet', value: 'snippet', width: 220 },
          ...Array.from(labelSet)
            .sort()
            .map(l => ({ text: l, value: l })),
          { text: 'Abstention', value: 'abstention' },
          { text: 'X', value: 'x' },
          { text: 'Total', value: 'total' },
          { text: 'Agreement', value: 'agreement' },
          { text: 'Conflict?', value: 'conflict', sortable: false }
        ]

        this.rows = data.map((r: any) => {
          const row: Record<string, any> = {
            id: r.id,
            snippet: r.snippet,
            total: r.total,
            agreement: r.agreement,
            abstention: r.abstention || 0,
            x: r.x || 0,
            decision: null // user decision placeholder
          }
          Object.entries(r.labels).forEach(([k, v]: [string, any]) => {
            row[k] = v
          })
          return row
        })

        // Load previously saved user decisions
        this.loadDecisions()
      } catch (err) {
        this.error = "Can't load preview"
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    onCancel() {
      const pid = this.$route.params.id
      this.$router.push(`/projects/${pid}/disagreements/diffs`)
    },
    onRestore() {
      this.localThreshold = this.initialThreshold
    },
    openConfirm() {
      this.confirmDialog = true
    },
    onConfirm() {
      const v = Math.max(0, Math.min(100, this.localThreshold))
      localStorage.setItem('disagreementThreshold', String(v))
      this.initialThreshold = v
      this.confirmDialog = false
      const pid = this.$route.params.id
      this.$router.push({
        path: '/message',
        query: {
          message: `Success! Threshold updated to ${v}%`,
          redirect: `/projects/${pid}/disagreements/diffs`
        }
      })
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
  transition: background-color 0.3s ease;
}

.low-agreement {
  background-color: rgba(255, 0, 0, 0.1) !important;
}

.conflict-icon {
  font-weight: 700;
  font-size: 1.3rem;
  line-height: 1;
  display: inline-block;
  width: 18px;
  text-align: center;
  cursor: pointer;
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
</style>