<template>
  <v-container fluid>
    <v-card class="mx-auto my-6" max-width="800">
      <v-card-title>Voting on Annotation rules</v-card-title>
      <v-card-text>
        <div v-if="loading" class="text--secondary">Loading history…</div>
        <div v-else>
          <v-radio-group v-model="selectedVersion" column>
            <v-radio
              v-for="item in history"
              :key="item.id"
              :label="`v${item.version} by ${item.author}`"
              :value="item.version"
              :disabled="userVotedVersions.includes(item.version)"
            />
          </v-radio-group>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn
          color="primary"
          :disabled="!selectedVersion || saving || userVotedVersions.includes(selectedVersion)"
          @click="submitVote"
        >
          Vote
        </v-btn>
        <v-btn text @click="openResultsDialog">Check Result</v-btn>
      </v-card-actions>
    </v-card>

    <v-dialog v-model="showResultsDialog" max-width="600">
      <v-card>
        <v-card-title>Voting Results</v-card-title>
        <v-card-text>
          <v-list two-line>
            <v-list-item v-for="res in results" :key="res.version">
              <v-list-item-content>
                <v-list-item-title>
                  v{{ res.version }} by {{ res.author }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  Votes: {{ res.votes }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="showResultsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { APIAnnotationRuleRepository } from '~/repositories/annotation-rule/apiAnnotationRuleRepository'

interface HistoryItem {
  id: number
  version: number
  author: string
}

interface ResultItem {
  version: number
  author: string
  votes: number
}

export default Vue.extend({
  layout: 'project',
  data() {
    return {
      history: [] as HistoryItem[],
      selectedVersion: null as number | null,
      loading: false,
      saving: false,
      showResultsDialog: false,
      results: [] as ResultItem[],
      userVotedVersions: [] as number[]
    }
  },
  async mounted() {
    this.loading = true
    try {
      const repo = new APIAnnotationRuleRepository()
      const grids = await repo.list(Number(this.$route.params.id))
      this.history = grids.map(g => ({
        id: g.id,
        version: g.version,
        author: g.createdBy
      }))
      this.initVoteState()
    } catch (e) {
      console.error('Failed to fetch voting history', e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    initVoteState() {
      const pid = Number(this.$route.params.id)
      const key = `annotation_rule_votes_${pid}`
      let votesMap: Record<string, any>
      try {
        votesMap = JSON.parse(localStorage.getItem(key) || '{}')
      } catch {
        votesMap = {}
      }
      const arr = votesMap[this.currentUsername]
      this.userVotedVersions = Array.isArray(arr) ? arr : []
    },
    submitVote() {
      if (!this.selectedVersion) return
      this.saving = true

      const pid = Number(this.$route.params.id)
      const key = `annotation_rule_votes_${pid}`
      let votesMap: Record<string, number[]> = {}
      try { votesMap = JSON.parse(localStorage.getItem(key) || '{}') } catch {}
      const me = this.currentUsername
      const userArr = Array.isArray(votesMap[me]) ? votesMap[me] : []
      if (!userArr.includes(this.selectedVersion)) userArr.push(this.selectedVersion)
      votesMap[me] = userArr
      localStorage.setItem(key, JSON.stringify(votesMap))
      this.userVotedVersions = userArr
      this.saving = false

      const votedVer = this.selectedVersion
      this.$router.push({
        path: '/message',
        query: {
          message: `Thank you for voting on version ${votedVer}!`,
          redirect: `/projects/${pid}/annotation-rules`
        }
      })
    },
    openResultsDialog() {
      const pid = Number(this.$route.params.id)
      const key = `annotation_rule_votes_${pid}`
      const votesMap = JSON.parse(localStorage.getItem(key) || '{}') as Record<string, number[]>
      const all = Object.values(votesMap).flat()

      this.results = this.history.map(h => ({
        version: h.version,
        author: h.author,
        votes: all.filter(v => v === h.version).length
      }))
      this.showResultsDialog = true
    }
  },
  computed: {
    currentUsername() {
      return this.$store.state.auth.username
    }
  }
})
</script>

<style scoped>
</style>