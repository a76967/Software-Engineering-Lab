<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title class="d-flex align-center">
        <span class="text-h5 font-weight-medium">Set Disagreement State</span>
        <v-spacer />
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          placeholder="Search snippet"
          hide-details
          dense
          clearable
          style="max-width:300px;"
        />
        <v-spacer />
        <v-btn text @click="onCancel">Cancel</v-btn>
        <v-btn text @click="onReset" :disabled="!hasChanged">Reset</v-btn>
        <v-btn text @click="applyThreshold" :disabled="thresholdDisabled">Threshold</v-btn>
        <v-btn color="primary" @click="onSave" :disabled="!hasChanged">Save</v-btn>
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
                  :style="{ height: item.agreement + '%',
                  background: agreementColorDisplay(item) }"
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

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.actions="{ item }">
            <v-btn text small @click="openDialog(item)">
              Set
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>

      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <v-dialog v-model="dialog" max-width="400">
        <v-card>
          <v-card-title>Set Disagreement State</v-card-title>
          <v-card-text>
            Is there a disagreement on this annotation?
            "<strong>{{ dialogItem?.snippet }}</strong>"?
          </v-card-text>
          <v-card-actions>
            <v-btn text @click="dialog = false">Cancel</v-btn>
            <v-spacer/>
            <v-btn
              color="red"
              text
              @click="applyDecision(true)"
              :disabled="conflictClass(dialogItem)==='red'"
            >Yes</v-btn>
            <v-btn
              color="green"
              text
              @click="applyDecision(false)"
              :disabled="conflictClass(dialogItem)==='green'"
            >No</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
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
      dialog: false as boolean,
      dialogItem: null as any,
      rows: [] as any[],
      headers: [] as any[],
      isLoading: false,
      confirmDialog: false,
      snackbar: false,
      decisionKey: '',
      search: '' as string,
      initialDefaults: {} as Record<number, boolean|null>
    }
  },

  computed: {
    filteredRows() {
      if (!this.search) return this.rows
      return this.rows.filter(r =>
        r.snippet.toLowerCase().includes(this.search.toLowerCase())
      )
    },
    hasChanged(): boolean {
      return this.rows.some(r => r.decision !== r.savedDecision)
    },

    thresholdDisabled(): boolean {
      return this.rows.length > 0 &&
        this.rows.every(r => r.decision === this.initialDefaults[r.id])
    }
  },

  mounted() {
    this.decisionKey = `disagreementDecisions:${this.$route.params.id}`
    this.fetchData()
  },

  methods: {
    toggleDecision(item: any) {
      const val = item.agreement
      const defaultSym = val >= this.localThreshold
        ? '✓' : val < this.localThreshold/2 ? '✗' : '⚠'
      if (defaultSym !== '⚠') return
      if (item.decision == null) item.decision = true
      else if (item.decision) item.decision = false
      else item.decision = null
    },

    openDialog(item: any) {
      this.dialogItem = item
      this.dialog = true
    },
    applyDecision(value: boolean) {
      this.dialogItem.decision = value
      this.dialog = false
    },

    onReset() {
      this.rows.forEach(r => { r.decision = r.savedDecision })
    },

    onCancel() {
      const pid = this.$route.params.id
      this.$router.push({
        path: this.localePath(`/projects/${pid}/disagreements/diffs`)
      })
    },

    onSave() {
      if (!this.hasChanged) return
      const pid = this.$route.params.id
      try {
        const decisions: Record<number, boolean> = {}
        this.rows.forEach(r => { decisions[r.id] = r.decision })

        localStorage.setItem(this.decisionKey, JSON.stringify(decisions))

        this.rows.forEach(r => { r.savedDecision = r.decision })

        this.$router.push({
          path: this.localePath('/message'),
          query: {
            message: 'Disagreements states set!',
            redirect: this.localePath(`/projects/${pid}/disagreements/diffs`)
          }
        })
      } catch (err) {
        console.error('Save failed:', err)
      }
    },

    conflictClass(item: any) {
      if (!item) return ''
      if (item.decision === true) return 'red'
      if (item.decision === false) return 'green'
      const v = item.agreement
      return v >= this.localThreshold
        ? 'green' : v < this.localThreshold/2 ? 'red' : 'orange'
    },
    conflictSymbol(item: any) {
      if (!item) return ''
      if (item.decision === true) return '✗'
      if (item.decision === false) return '✓'
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
        data.forEach((r: any) =>
          Object.keys(r.labels).forEach(l => labelSet.add(l))
        )
        const labelArray = Array.from(labelSet).sort()

        this.headers = [
          { text: 'Snippet',     value: 'snippet',  width: 250 },
          ...labelArray.map(l => ({ text: l, value: l })),
          { text: 'Abstention',  value: 'abstention', sortable: false },
          { text: 'X',           value: 'x',           sortable: false },
          { text: 'Agreement %', value: 'agreement',   sortable: false },
          { text: 'State',       value: 'conflict',    sortable: false },
          { text: 'Actions',     value: 'actions',     sortable: false }
        ]

        this.rows = data.map((r: any) => {
          const row: Record<string, any> = {
            id: r.id,
            snippet: r.snippet,
            abstention: r.abstention || 0,
            x: r.x || 0,
            agreement: r.agreement,
            decision: r.decision
          }
          labelArray.forEach(l => {
            row[l] = (r.labels[l] != null ? r.labels[l] : 0)
          })
          return row
        })

        const initDefs: Record<number, boolean|null> = {}
        this.rows.forEach(r => {
          const t = r.agreement >= this.localThreshold
            ? false
            : r.agreement < this.localThreshold/2
              ? true
              : null
          initDefs[r.id] = t
        })
        this.initialDefaults = initDefs

        const stored = localStorage.getItem(this.decisionKey) || '{}'
        const savedDecisions: Record<number, boolean> = JSON.parse(stored)
        this.rows.forEach(r => {
          if (savedDecisions[r.id] != null) {
            r.decision = savedDecisions[r.id]
          } else {
            r.decision = this.initialDefaults[r.id]
          }
          r.savedDecision = r.decision
        })
      } catch (err) {
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    applyThreshold() {
      this.rows.forEach(r => {
        if (r.agreement >= this.localThreshold)      r.decision = false
        else if (r.agreement < this.localThreshold/2) r.decision = true
        else                                         r.decision = null
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
  transition: border-color 0.3s ease;
}
.agreement-fill {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  transition: background 0.3s ease;
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