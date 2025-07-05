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

            <div v-else>
              <v-row class="my-6">
                <v-col cols="6" class="text-center">
                  <div
                    class="display-2 font-weight-bold"
                    :style="{ color: datasetCount > 0 ? statusColor : '#4caf50' }"
                  >
                    {{ datasetCount }}
                  </div>
                  <div class="subtitle-1 text--secondary">
                    {{ datasetCount === 1 ? 'Dataset' : 'Datasets' }} with disagreements
                  </div>
                </v-col>
                <v-col cols="6" class="text-center" v-if="summary.length">
                  <div
                    class="display-2 font-weight-bold"
                    :style="{ color: statusColor }"
                  >
                    {{ averageAgreement }}%
                  </div>
                  <div class="subtitle-1 text--secondary">Average agreement % on all datasets</div>
                </v-col>
              </v-row>

              <v-divider v-if="summary.length" class="my-4" />

              <div v-if="summary.length === 0" class="text-center py-6">
                <v-icon
                  size="80"
                  :color="statusColor"
                  class="mb-4"
                  :icon="mdiCheckCircle"
                />
                <div class="headline font-weight-medium">Perfect Agreement!</div>
                <div class="subtitle-1 text--secondary">
                  All annotators are in sync on this project.
                </div>
              </div>

              <div v-else>
                <v-alert
                  dense
                  :type="averageAgreement >= 80
                    ? 'success'
                    : averageAgreement >= 40
                      ? 'warning'
                      : 'error'"
                  class="my-2"
                >
                  {{
                    averageAgreement >= 80
                      ? 'Good agreement levels detected!'
                      : averageAgreement >= 40
                        ? 'Moderate disagreement levels – review recommended!'
                        : 'High disagreement levels – immediate review needed!!'
                  }}
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
            <v-btn
              v-else-if="!isLoading"
              text
              @click="goToDiffs"
            >
              <v-icon left :icon="mdiEye" /> View Details
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
    averageAgreement(): number {
      if (!this.summary.length) return 0
      const total = this.summary.reduce((acc, r) => acc + (r.agreement || 0), 0)
      return Math.round(total / this.summary.length)
    },
    statusColor(): string {
      if (this.averageAgreement >= 80) return '#4caf50'
      if (this.averageAgreement >= 40) return '#ff9800'
      return '#f44336'
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
</style>