<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="8">
        <v-card class="my-6" max-width="800">
          <v-card-title>
            Voting on Annotation rules
            <v-spacer />
            <span v-if="meta">Ends in {{ timeRemaining }}</span>
          </v-card-title>
          <v-card-text>
            <div v-if="loading" class="text--secondary">Loading history…</div>
            <div v-else>
              <v-radio-group v-model="selectedVersion" column>
                <v-radio
                  v-for="item in history"
                  :key="item.id"
                  :label="`v${item.version} by ${item.author}`"
                  :value="item.version"
                  :disabled="userVotedVersions.includes(item.version) || voteClosed"
                />
              </v-radio-group>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
            <v-btn
              color="primary"
              :disabled="!selectedVersion || 
              saving || voteClosed || userVotedVersions.includes(selectedVersion)"
              @click="submitVote"
            >
              Vote
            </v-btn>
            <v-btn text @click="openResultsDialog">Results</v-btn>
            <v-btn
              v-if="isAdmin && !voteClosed"
              text
              color="error"
              @click="closeVote"
            >
              Close Vote
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-card class="my-6" max-width="800">
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
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="my-6">
          <v-card-title>
            Rules
            <v-spacer/>
            <span>v{{ selectedVersion || '-' }}</span>
          </v-card-title>
          <v-card-text>
            <div v-if="rulesLoading" class="text--secondary">Loading…</div>
            <v-list two-line v-else>
              <v-list-item
                v-for="(rule, idx) in currentRules"
                :key="idx"
                class="rule-item"
              >
                <v-list-item-content>
                  <v-list-item-title>
                    {{ idx + 1 }}. {{ rule }}
                  </v-list-item-title>
                </v-list-item-content>
                <v-list-item-action v-if="canEditCurrent">
                  <v-btn icon small @click="startEdit(idx)">
                    <v-icon small>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn icon small @click="removeRule(idx)">
                    <v-icon small color="error">mdi-delete</v-icon>
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </v-list>
            <div v-if="canEditCurrent" class="mt-4">
              <v-text-field
                v-model="newRule"
                label="New rule"
                dense
                hide-details
                @keyup.enter="addRule"
              />
              <v-btn small color="primary" 
              class="mr-2" @click="addRule" :disabled="!newRule.trim()">
                Add
              </v-btn>
              <v-btn small color="success" @click="saveRules" :loading="savingRules" 
              :disabled="savingRules">
                Save
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

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
      userVotedVersions: [] as number[],
      rulesLoading: false,
      currentRules: [] as string[],
      newRule: '' as string,
      savingRules: false,
      isAdmin: false,
      meta: null as { start: number; end: number; phase: number } | null
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
      if (this.history.length) {
        this.selectedVersion = this.history[0].version
        await this.fetchRules(this.history[0].id)
      }
      await this.fetchRole()
      this.loadMeta()
    } catch (e) {
      console.error('Failed to fetch voting history', e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    async fetchRole() {
      try {
        const member = await this.$repositories.member.fetchMyRole(this.$route.params.id)
        this.isAdmin = member.isProjectAdmin
      } catch (e) {
        console.error('Failed to fetch role', e)
      }
    },
    loadMeta() {
      const pid = Number(this.$route.params.id)
      const key = `annotation_rule_vote_meta_${pid}`
      const now = Date.now()
      try {
        const m = JSON.parse(localStorage.getItem(key) || 'null')
        if (m && m.end && now < m.end) {
          this.meta = m
          return
        }
      } catch {}
      this.meta = { start: now, end: now + 24 * 60 * 60 * 1000, phase: 1 }
      localStorage.setItem(key, JSON.stringify(this.meta))
    },
    saveMeta() {
      const pid = Number(this.$route.params.id)
      const key = `annotation_rule_vote_meta_${pid}`
      localStorage.setItem(key, JSON.stringify(this.meta))
    },
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
    async fetchRules(id: number) {
      this.rulesLoading = true
      try {
        const repo = new APIAnnotationRuleRepository()
        const grid = await repo.get(Number(this.$route.params.id), id)
        this.currentRules = grid.rules
      } catch (e) {
        console.error('Failed to load rules', e)
        this.currentRules = []
      } finally {
        this.rulesLoading = false
      }
    },
    addRule() {
      const t = this.newRule.trim()
      if (!t) return
      this.currentRules.push(t)
      this.newRule = ''
    },
    startEdit(idx: number) {
      this.newRule = this.currentRules[idx]
      this.currentRules.splice(idx, 1)
    },
    removeRule(idx: number) {
      this.currentRules.splice(idx, 1)
    },
    async saveRules() {
      if (!this.currentRules.length) return
      this.savingRules = true
      try {
        const repo = new APIAnnotationRuleRepository()
        await repo.create(Number(this.$route.params.id), this.currentRules)
        this.$router.push({
          path: '/message',
          query: {
            message: 'Rules updated!',
            redirect: `/projects/${this.$route.params.id}/annotation-rules`
          }
        })
      } catch (e) {
        console.error('Failed to save rules', e)
      } finally {
        this.savingRules = false
      }
    },
    closeVote() {
      if (!this.meta) return
      this.meta.end = Date.now()
      this.saveMeta()
    },
    submitVote() {
      if (!this.selectedVersion || this.voteClosed) return
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
    voteClosed(): boolean {
      return !!(this.meta && Date.now() > this.meta.end)
    },
    timeRemaining(): string {
      if (!this.meta) return ''
      const diff = this.meta.end - Date.now()
      if (diff <= 0) return 'ended'
      const mins = Math.floor(diff / 60000)
      const hrs = Math.floor(mins / 60)
      const m = mins % 60
      return `${hrs}h ${m}m`
    },
    canEditCurrent(): boolean {
      return this.isAdmin && !this.voteClosed && this.voteCountForCurrent === 0
    },
    voteCountForCurrent(): number {
      const pid = Number(this.$route.params.id)
      const key = `annotation_rule_votes_${pid}`
      const votesMap = JSON.parse(localStorage.getItem(key) || '{}') as Record<string, number[]>
      const all = Object.values(votesMap).flat()
      return this.selectedVersion ? all.filter(v => v === this.selectedVersion).length : 0
    },
    currentUsername() {
      return this.$store.state.auth.username
    }
  },
  watch: {
    selectedVersion(val) {
      const item = this.history.find(h => h.version === val)
      if (item) this.fetchRules(item.id)
    }
  }
})
</script>

<style scoped>
</style>