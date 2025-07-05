<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="my-6" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon left large :color="statusColor">mdi-alert-circle</v-icon>
            <span class="text-h6 font-weight-medium">Disagreements Summary</span>
            <v-spacer />
          </v-card-title>

          <v-card-text>
            <div v-if="isLoading" class="text-center my-8">
              <v-progress-circular indeterminate color="primary" size="60" />
              <div class="mt-3 text--secondary">Loading disagreements...</div>
            </div>

            <v-alert v-else-if="error" type="error" outlined class="mt-4">
              <v-icon left>mdi-database-alert</v-icon>
              {{ error }}
            </v-alert>

            <!-- No annotations available -->
            <div v-if="summary.length === 0" class="text-center py-6">
              <v-icon size="80" :icon="mdiAlertCircle" color="grey lighten-1" class="mb-4"/>
              <div class="headline font-weight-medium">No annotations yet</div>
              <div class="subtitle-1 text--secondary">
                There are currently not enough annotations in this project,
                so it's not possible to determine disagreements.
              </div>
            </div>

            <!-- Summary exists -->
            <div v-else>
              <!-- Counts & Agreement -->
              <v-row class="my-6" align="center">
                <v-col cols="6" class="text-center d-flex flex-column justify-center">
                  <div class="display-2 font-weight-bold" :style="{ color: datasetColor }">
                    {{ datasetCount }}
                  </div>
                  <div class="subtitle-1 text--secondary">
                    {{ datasetCount === 1 ? 'Dataset' : 'Datasets' }} with disagreements
                  </div>
                </v-col>
                <v-col cols="6" class="text-center d-flex flex-column justify-center">
                  <div class="d-flex justify-center">
                    <div
                      class="agreement-fill-circle index-agreement"
                      :style="{ borderColor: averageColor }"
                    >
                      <div
                        class="agreement-fill"
                        :style="{ height: averageAgreement + '%', background: averageColor }"
                      ></div>
                      <span class="agreement-label">{{ averageAgreement }}%</span>
                    </div>
                  </div>
                  <div class="subtitle-1 text--secondary">
                    Average agreement % on all datasets
                  </div>
                </v-col>
              </v-row>

              <v-divider class="my-4"/>

              <!-- Perfect agreement when there are datasets but zero disagreements -->
              <div v-if="datasetCount === 0" class="text-center py-6">
                <v-icon size="80" :color="statusColor" :icon="mdiCheckCircle"/>
                <div class="headline font-weight-medium">Perfect Agreement!</div>
                <div class="subtitle-1 text--secondary">
                  All annotators are in sync on this project.
                </div>
              </div>

              <!-- Disagreements summary alert -->
              <div v-else>
                <v-alert dense :type="alertType" class="my-2" :style="alertStyle">
                  {{ alertMessage }}
                </v-alert>
              </div>
            </div>
          </v-card-text>

          <v-card-actions class="justify-end">
            <v-btn
              v-if="!isLoading && summary.length"
              color="primary"
              large
              @click="goToDiffs"
            >
              Check Disagreements
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'
import {
  mdiThumbUp,
  mdiAlert,
  mdiAlertCircle,
  mdiCheckCircle,
  mdiMagnify,
  mdiEye
} from '@mdi/js'

export default Vue.extend({
  name: 'DisagreementsLanding',
  layout: 'project',
  data() {
    return {
      summary: [] as any[],
      isLoading: false,
      error: '',
      mdiThumbUp,
      mdiAlert,
      mdiAlertCircle,
      mdiCheckCircle,
      mdiMagnify,
      mdiEye
    }
  },
  computed: {
    /** alias averageColor so existing bindings to statusColor continue */
    statusColor(): string {
      return this.averageColor
    },

    datasetCount(): number {
      const pid = this.$route.params.id
      const raw = localStorage.getItem(`disagreementDecisions:${pid}`)
      let decisions: Record<string, boolean> = {}
      if (raw) {
        try {
          decisions = JSON.parse(raw)
        } catch (err) {
          console.error('failed to parse decisions', err)
        }
      }

      const storedThreshold = localStorage.getItem('disagreementThreshold')
      const threshold = storedThreshold ? parseInt(storedThreshold) : 80

      return this.summary.filter(r => {
        const decision = decisions[r.id]
        if (decision === false) return false
        if (decision === true) return true
        return r.agreement < threshold
      }).length
    },
    datasetPercent(): number {
      if (!this.summary.length) return 0
      return Math.round((this.datasetCount / this.summary.length) * 100)
    },
    datasetState(): 'green'|'orange'|'red' {
      if (this.datasetPercent < 40) return 'green'
      if (this.datasetPercent < 80) return 'orange'
      return 'red'
    },
    datasetColor(): string {
      return this.datasetState === 'green'
        ? '#4caf50'
        : this.datasetState === 'orange'
          ? '#ff9800'
          : '#f44336'
    },
    averageAgreement(): number {
      if (!this.summary.length) return 0
      const total = this.summary.reduce((acc, r) => acc + (r.agreement || 0), 0)
      return Math.round(total / this.summary.length)
    },
    averageState(): 'green'|'orange'|'red' {
      return this.averageAgreement >= 80
        ? 'green'
        : this.averageAgreement >= 40
          ? 'orange'
          : 'red'
    },
    averageColor(): string {
      return this.averageState === 'green'
        ? '#4caf50'
        : this.averageState === 'orange'
          ? '#ff9800'
          : '#f44336'
    },
    alertType(): 'success' | 'warning' | 'error' {
      const d = this.datasetState
      const a = this.averageState
      if (d === 'green' && a === 'green')      return 'success'
      if (d === 'green' && a === 'orange')     return 'warning'
      if (d === 'green' && a === 'red')        return 'error'
      if (d === 'orange' && a === 'green')     return 'warning'
      if (d === 'orange' && a === 'orange')    return 'warning'
      if (d === 'orange' && a === 'red')       return 'error'
      if (d === 'red' && a === 'green')        return 'warning'
      if (d === 'red' && a === 'orange')       return 'error'
      return 'error'
    },
    alertStyle(): Record<string, string> {
      return {
        background: `linear-gradient(to right,
          ${this.datasetColor} 0%,
          ${this.averageColor} 100%)`,
        color: 'white'
      }
    },
    alertMessage(): string {
      const d = this.datasetState
      const a = this.averageState
      if (d==='green'&&a==='green')   return 'All Good: no disagreements & high agreement %.'
      if (d==='green'&&a==='orange')  return 'No disagreements but moderate agreement %.'
      if (d==='green'&&a==='red')     return 'No disagreements but low agreement %: Review data.'
      if (d==='orange'&&a==='green')  return 'Some disagreements detected, but agreement % is high.'
      if (d==='orange'&&a==='orange') return 'Some disagreements and moderate agreement %: Review recommended.'
      if (d==='orange'&&a==='red')    return 'Disagreements present and low agreement %: Immediate review needed.'
      if (d==='red'&&a==='green')     return 'Mostly disagreements but agreement % high? Inspect inconsistencies.'
      if (d==='red'&&a==='orange')    return 'Mostly disagreements and moderate agreement %: Urgent review required.'
      return 'Critical: Mostly disagreements & low agreement %: Immediate attention required.'
    }
  },
  mounted() {
    this.fetchSummary()
  },
  methods: {
    async fetchSummary() {
      this.isLoading = true
      const pid = this.$route.params.id
      try {
        const { data } = await axios.get(`/v1/projects/${pid}/metrics/span-disagreements`)
        this.summary = data || []
      } catch (err) {
        console.error('failed to load summary', err)
        this.error = "Error: Can't access our database!"
      } finally {
        this.isLoading = false
      }
    },
    goToDiffs() {
      const pid = this.$route.params.id
      this.$router.push(`/projects/${pid}/disagreements/diffs`)
    }
  }
})
</script>

<style scoped>
.display-2 {
  font-size: 2.75rem;
}

.agreement-fill-circle {
  position: relative;
  width: 120px;
  height: 120px;
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
  transition: height 0.3s ease;
}
.agreement-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 2.75rem;
  font-weight: 600;
}
.index-agreement {
  width: 120px;
  height: 120px;
}
</style>