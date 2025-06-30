<template>
    <v-container fluid class="pa-4">
      <v-card flat>
        <v-card-title class="d-flex align-center">
          <span class="text-h5 font-weight-medium">Set Disagreement Threshold</span>
        </v-card-title>
  
        <!-- slider + numeric input -->
        <v-row class="align-center mb-6">
          <v-col cols="11" class="py-0">
            <v-slider v-model="localThreshold" :min="0" :max="100" step="1" />
          </v-col>
  
          <v-col cols="1" class="py-0 pr-8 d-flex align-center">
            <v-text-field
              v-model.number="localThreshold"
              type="number"
              min="0"
              max="100"
              step="1"
              dense
              hide-details
              suffix="%"
              style="width:70px"
            />
          </v-col>
        </v-row>
  
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
          <!-- agreement column -->
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
  
          <!-- conflict column -->
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.conflict="{ item }">
            <span
              class="conflict-icon"
              :class="conflictClass(item.agreement)"
            >
              {{ conflictSymbol(item.agreement) }}
            </span>
          </template>
  
          <!-- snippet column -->
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
  
        <v-card-actions>
          <v-spacer/>
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
  
        <!-- confirm dialog -->
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
              <v-spacer/>
              <v-btn text @click="confirmDialog=false">No</v-btn>
              <v-btn color="primary" @click="onConfirm">Yes</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
  
        <!-- toast -->
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
      const stored = localStorage.getItem('disagreementThreshold')
      const init   = stored ? parseInt(stored) : 80
      return {
        initialThreshold: isNaN(init) ? 80 : init,
        localThreshold:   isNaN(init) ? 80 : init,
        rows:      [] as any[],
        headers:   [] as any[],
        isLoading: false,
        error:     '',
        confirmDialog: false,
        snackbar:  false
      }
    },
  
    watch: {
      localThreshold(val) {
        const num = Math.max(0, Math.min(100, Number(val) || 0))
        if (num !== val) {
          this.$nextTick(() => { this.localThreshold = num })
          return
        }
        this.fetchData()
      }
    },
  
    mounted() {
      this.fetchData()
    },
  
    methods: {
      conflictClass(val:number) {
        return val >= this.localThreshold ? 'green'
             : val <  this.localThreshold/2 ? 'red'
             : 'orange'
      },
      conflictSymbol(val:number) {
        return val >= this.localThreshold      ? '✓'
             : val <  this.localThreshold/2   ? '✗'
             : '⚠'
      },
  
      rowClass(item:any) {
        return item.agreement < this.localThreshold / 2 ? 'low-agreement' : ''
      },
      agreementColor(val:number) {
        if (val >= this.localThreshold)     return 'green'
        if (val >= this.localThreshold/2)   return 'orange'
        return 'red'
      },
  
      async fetchData() {
        this.isLoading = true
        const pid = Number(this.$route.params.id)
        try {
          const { data } = await axios.get(
            `/v1/projects/${pid}/metrics/span-disagreements`
          )
          const labelSet = new Set<string>()
          data.forEach((r:any) =>
            Object.keys(r.labels).forEach(l => labelSet.add(l))
          )
          this.headers = [
            { text:'Snippet', value:'snippet', width:220 },
            ...Array.from(labelSet).sort().map(l => ({ text:l, value:l })),
            { text:'Abstention', value:'abstention' },
            { text:'X',          value:'x' },
            { text:'Total',      value:'total' },
            { text:'Agreement',  value:'agreement' },
            { text:'Conflict?',  value:'conflict', sortable:false }
          ]
          this.rows = data.map((r:any) => {
            const row:Record<string,any> = {
              snippet:    r.snippet,
              total:      r.total,
              agreement:  r.agreement,
              abstention: r.abstention||0,
              x:          r.x||0
            }
            Object.entries(r.labels).forEach(([k,v]:[string,any]) => { row[k]=v })
            return row
          })
        } catch {
          this.error = "Can't load preview"
        } finally {
          this.isLoading = false
        }
      },
  
      onCancel()  { this.$router.back() },
      onRestore() { this.localThreshold = this.initialThreshold },
      openConfirm(){ this.confirmDialog = true },
      onConfirm() {
        const v = Math.max(0, Math.min(100, this.localThreshold))
        localStorage.setItem('disagreementThreshold', String(v))
        this.initialThreshold = v
        this.confirmDialog = false
        this.$router.push({
          path: '/message',
          query: {
            message: `Success! Threshold updated to ${v}%`,
            redirect: this.$route.fullPath
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