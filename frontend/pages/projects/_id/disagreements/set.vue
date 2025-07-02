<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title class="d-flex align-center">
        <span class="text-h5 font-weight-medium">Set Disagreement</span>
        <v-spacer />
        <v-btn text @click="onReset" :disabled="!hasChanged">Reset</v-btn>
        <v-btn color="primary" @click="onSave" :disabled="!hasChanged">Save</v-btn>
      </v-card-title>

      <v-card-text class="pa-0">
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
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.agreement="{ item }">
            <div class="d-flex justify-center">
              <div
                class="agreement-fill-circle"
                :style="{ borderColor: agreementColor(item.agreement) }"
              >
                <div
                  class="agreement-fill"
                  :style="{ height: item.agreement + '%', 
                  background: agreementColor(item.agreement) }"
                ></div>
                <span class="agreement-label">{{ item.agreement }}%</span>
              </div>
            </div>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.conflict="{ item }">
            <v-btn
              icon small
              class="pa-0 ma-0"
              @click.stop="toggleDecision(item)"
            >
              <span class="conflict-icon" :class="conflictClass(item)">
                {{ conflictSymbol(item) }}
              </span>
            </v-btn>
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
  name: 'DisagreementThresholdPage',
  layout: 'project',

  data() {
    const stored = localStorage.getItem('disagreementThreshold')
    const init = stored ? parseInt(stored, 10) : 80
    return {
      initialThreshold: isNaN(init) ? 80 : init,
      localThreshold: isNaN(init) ? 80 : init,
      rows: [] as any[],
      headers: [] as any[],
      isLoading: false,
      confirmDialog: false,
      snackbar: false
    }
  },

  computed: {
    // enable Save/Reset only when at least one decision made
    hasChanged(): boolean {
      return this.rows.some(r => r.decision !== null && r.decision !== undefined)
    }
  },

  mounted() {
    this.fetchData()
  },

  methods: {
    // cycle decision only for orange cases
    toggleDecision(item: any) {
      const val = item.agreement
      const defaultSym = val >= this.localThreshold
        ? '✓' : val < this.localThreshold/2 ? '✗' : '⚠'
      if (defaultSym !== '⚠') return
      if (item.decision == null) item.decision = true
      else if (item.decision) item.decision = false
      else item.decision = null
    },

    conflictClass(item: any) {
      if (item.decision === true) return 'green'
      if (item.decision === false) return 'red'
      const v = item.agreement
      return v >= this.localThreshold
        ? 'green' : v < this.localThreshold/2 ? 'red' : 'orange'
    },
    conflictSymbol(item: any) {
      if (item.decision === true) return '✓'
      if (item.decision === false) return '✗'
      const v = item.agreement
      return v >= this.localThreshold
        ? '✓' : v < this.localThreshold/2 ? '✗' : '⚠'
    },
    rowClass(item: any) {
      return item.decision === false || item.agreement < this.localThreshold/2
        ? 'low-agreement' : ''
    },
    agreementColor(val: number) {
      if (val >= this.localThreshold) return 'green'
      if (val >= this.localThreshold/2) return 'orange'
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
          { text: 'Snippet', value: 'snippet', width: 250 },
          ...Array.from(labelSet).sort().map(l => ({ text: l, value: l })),
          { text: 'Abstention', value: 'abstention', sortable: false },
          { text: 'X', value: 'x', sortable: false },
          { text: 'Agreement', value: 'agreement', sortable: false },
          { text: 'Conflict?', value: 'conflict', sortable: false }
        ]
        this.rows = data.map((r: any) => ({
          ...r.labels,
          id: r.id,
          snippet: r.snippet,
          abstention: r.abstention || 0,
          x: r.x || 0,
          agreement: r.agreement,
          decision: null
        }))
      } catch (e) {
        console.error(e)
      } finally {
        this.isLoading = false
      }
    },

    onReset() {
      this.rows.forEach(r => { r.decision = null })
    },
    async onSave() {
      const updates = this.rows
        .filter(r => r.decision != null)
        .map(r => ({ id: r.id, decision: r.decision }))
      await axios.post(
        `/v1/projects/${this.$route.params.id}/disagreements/decisions/`,
        { decisions: updates }
      )
      this.snackbar = true
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
.conflict-icon.green { color: #4caf50; }
.conflict-icon.orange { color: #ff9800; }
.conflict-icon.red    { color: #f44336; }

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