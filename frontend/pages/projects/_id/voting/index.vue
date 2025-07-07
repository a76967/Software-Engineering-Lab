<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="8">
        <v-card class="my-6" max-width="800">
          <v-card-title>
            Voting on Annotation rules
            <v-spacer />
            <!-- show countdown until end, or “Ended” once closed -->
            <span v-if="meta && !voteClosed">Ends in {{ timeRemaining }}</span>
            <span v-else-if="meta && voteClosed">Ended</span>
          </v-card-title>
          <v-card-text>
            <div v-if="loading" class="text--secondary">Loading history…</div>
            <div v-else>
              <template v-if="voteClosed">
                <div class="text--secondary">
                  The Voting on Annotation rules has been closed, check the results below.
                </div>
              </template>
              <template v-else>
                <div class="mt-4">
                  <div v-if="rulesLoading" class="text--secondary">Loading…</div>
                  <template v-else>
                    <v-card
                      v-for="(rule, idx) in currentRules"
                      :key="idx"
                      class="mb-2"
                      outlined
                    >
                      <v-card-title>#{{ idx + 1 }} - {{ rule }}</v-card-title>
                      <v-card-actions>
                        <v-spacer />
                        <v-btn small icon @click="viewRule(rule, idx)">
                          <v-icon small>mdi-eye</v-icon>
                        </v-btn>
                        <v-btn
                          text
                          color="green"
                          :disabled="!!userRuleVotes[idx]"
                          @click="voteRule(idx, 'up')"
                        >
                          Approve
                        </v-btn>
                        <v-btn
                          text
                          color="red"
                          :disabled="!!userRuleVotes[idx]"
                          @click="voteRule(idx, 'down')"
                        >
                          Reject
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </template>
                </div>
              </template>
            </div>
          </v-card-text>
        </v-card>

        <v-card class="my-6" max-width="800">
          <v-card-title>Voting Results</v-card-title>
          <v-card-text>
            <div v-if="currentRules.length === 0" class="text--secondary">No rules</div>
            <div v-else>
              <div v-if="!voteClosed" class="text--secondary mb-2">
                The Voting is still ongoing, results may change.
              </div>
              <v-card
                v-for="(rule, idx) in currentRules"
                :key="idx"
                class="mb-2"
                outlined
              >
                <v-card-title class="d-flex justify-space-between align-center">
                  <div>#{{ idx + 1 }} - {{ rule }}</div>
                  <v-chip
                    :color="ruleResults[idx] &&
                    ruleResults[idx].up >= ruleResults[idx].down ? 'green' : 'red'"
                    text-color="white"
                    small
                  >
                    {{ ruleResults[idx] && ruleResults[idx].up >=
                    ruleResults[idx].down ? 'Approved' : 'Rejected' }}
                  </v-chip>
                </v-card-title>
                    <v-card-text>
                      {{ ruleResults[idx]?.up || 0 }} <span class="green--text">Approve</span>
                      {{ ruleResults[idx]?.down || 0 }} <span class="red--text">Reject</span>
                    </v-card-text>
                </v-card>
              </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="my-6">
          <v-card-title>
            Rules
            <v-spacer/>
            <v-btn
              v-if="canEditCurrent"
              icon
              size="small"
              class="ml-2"
              @click="scrollToAddInput"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="rulesLoading" class="text--secondary">Loading…</div>
            <div v-else>
              <v-card
                v-for="(rule, idx) in editRules"
                :key="idx"
                class="mb-2"
                outlined
              >
                <v-card-title class="d-flex justify-space-between">
                  <div>#{{ idx + 1 }} - {{ rule }}</div>
                  <v-btn small icon @click="viewRule(rule, idx)">
                    <v-icon small>mdi-eye</v-icon>
                  </v-btn>
                </v-card-title>
                <v-card-actions v-if="canEditCurrent">
                  <v-spacer />
                  <v-btn icon small @click="startEdit(idx)">
                    <v-icon small>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn icon small @click="removeRule(idx)">
                    <v-icon small color="error">mdi-delete</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </div>
            <div v-if="canEditCurrent" class="mt-4">
              <v-text-field
                v-model="newRule"
                id="new-rule-input"
                label="New rule"
                outlined
                shaped
                append-icon="mdi-close-circle"
                @click:append="newRule = ''"
                class="mb-2"
                @keyup.enter="addRule"
              />
              <div class="d-flex align-center mb-1">
                <v-btn
                  small
                  color="primary"
                  class="me-3"
                  :disabled="!newRule.trim()"
                  @click="addRule"
                >
                  Add Rule
                </v-btn>
                <v-btn
                  small
                  color="success"
                  :loading="savingRules"
                  :disabled="savingRules"
                  @click="saveRules"
                >
                  Save
                </v-btn>
              </div>
            </div>
          </v-card-text>
        </v-card>

        <v-card class="my-6">
          <v-card-title>
            Voting Period
            <v-spacer/>
            <template v-if="voteClosed">
              <v-chip color="red" text-color="white" small>Voting Ended</v-chip>
            </template>
            <span v-else-if="meta" class="period-dates">
              {{ formattedStart }} - {{ formattedEnd }}</span>
            <span v-else class="text--secondary">
              Undefined
            </span>
          </v-card-title>
          <v-card-actions>
            <v-spacer/>
            <v-btn
              v-if="isAdmin && !voteClosed"
              text
              color="primary"
              class="me-2"
              @click="openEditDialog"
            >
              <v-icon left small>mdi-pencil</v-icon>
              {{ meta ? 'Edit' : 'Set' }}
            </v-btn>
            <v-btn
              v-if="isAdmin && meta && !voteClosed"
              text
              color="error"
              @click="closeVote"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="showResultsDialog" max-width="600">
      <v-card>
        <v-card-title>Voting Results</v-card-title>
        <v-card-text>
          <div v-if="currentRules.length === 0" class="text--secondary">No rules</div>
          <div v-else>
            <div v-if="!voteClosed" class="text--secondary mb-2">
              The Voting is still ongoing, results may change.
            </div>
            <v-card
              v-for="(rule, idx) in currentRules"
              :key="idx"
              class="mb-2"
              outlined
            >
              <v-card-title class="d-flex justify-space-between align-center">
                <div>#{{ idx + 1 }} - {{ rule }}</div>
                <v-chip
                  :color="ruleResults[idx] && ruleResults[idx].up
                  >= ruleResults[idx].down ? 'green' : 'red'"
                  text-color="white"
                  small
                >
                  {{ ruleResults[idx] && ruleResults[idx].up
                  >= ruleResults[idx].down ? 'Approved' : 'Rejected' }}
                </v-chip>
              </v-card-title>
              <v-card-text>
                {{ ruleResults[idx]?.up || 0 }} <span class="green--text">Approve</span>
                {{ ruleResults[idx]?.down || 0 }} <span class="red--text">Reject</span>
              </v-card-text>
            </v-card>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="showResultsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showRuleDialog" max-width="500">
      <v-card>
        <v-card-title>Rule #{{ selectedRuleIndex + 1 }}</v-card-title>
        <v-card-text>
          <div>{{ selectedRuleText }}</div>
          <div class="text--secondary">Author: {{ currentAuthor }}</div>
          <div class="text--secondary">Submitted: {{ formattedSubmitted }}</div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="showRuleDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="editDialog" persistent max-width="600">
      <v-card>
        <v-card-title>Edit Voting Period</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-menu
                v-model="startMenu"
                :close-on-content-click="false"
                offset-y
                transition="scale-transition"
              >
                <template #activator="{ attrs, on }">
                  <v-text-field
                    v-model="editStart"
                    label="Start"
                    prepend-icon="mdi-clock-outline"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                  />
                </template>
                <v-card>
                  <v-date-picker v-model="startDate" no-title scrollable/>
                  <v-time-picker v-model="startTime" format="24hr"/>
                  <v-card-actions>
                    <v-spacer/>
                    <v-btn text color="primary" @click="applyStart">OK</v-btn>
                  </v-card-actions>
                </v-card>
              </v-menu>
            </v-col>
            <v-col cols="12" md="6">
              <v-menu
                v-model="endMenu"
                :close-on-content-click="false"
                offset-y
                transition="scale-transition"
              >
                <template #activator="{ attrs, on }">
                  <v-text-field
                    v-model="editEnd"
                    label="End"
                    prepend-icon="mdi-clock-outline"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                  />
                </template>
                <v-card>
                  <v-date-picker v-model="endDate" no-title scrollable/>
                  <v-time-picker v-model="endTime" format="24hr"/>
                  <v-card-actions>
                    <v-spacer/>
                    <v-btn text color="primary" @click="applyEnd">OK</v-btn>
                  </v-card-actions>
                </v-card>
              </v-menu>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="editDialog = false">Cancel</v-btn>
          <v-btn color="primary" text @click="saveEditPeriod">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { APIAnnotationRuleRepository } from '~/repositories/annotation-rule/apiAnnotationRuleRepository'
import { APIRuleVoteRepository } from '@/repositories/annotation-rule/apiRuleVoteRepository'
import { APIGridVoteRepository } from '~/repositories/annotation-rule/apiGridVoteRepository'

interface HistoryItem {
  id: number
  version: number
  author: string
  rule: string
}

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data() {
    return {
      history: [] as HistoryItem[],
      selectedVersion: null as number | null,
      loading: false,
      saving: false,
      showResultsDialog: false,
      userVotedVersions: [] as number[],
      rulesLoading: false,
      currentRules: [] as string[],
      editRules: [] as string[],
      currentRulesAuthor: '' as string,
      currentRulesSubmitted: '' as string,
      newRule: '' as string,
      savingRules: false,
      isAdmin: false,
      currentGridId: null as number | null,
      meta: null as { start: number; end: number; phase: number; closed: boolean } | null,
      showRuleDialog: false,
      selectedRuleText: '',
      selectedRuleIndex: -1,
      editDialog: false,
      editStart: '',
      editEnd: '',
      ruleResults: {} as Record<number, { up: number; down: number }>,
      userRuleVotes: {} as Record<number, string>,
      versionVoteCounts: {} as Record<number, number>,
      startMenu: false,
      endMenu: false,
      startDate: '',
      startTime: '',
      endDate: '',
      endTime: ''
    }
  },
  computed: {
    voteClosed(): boolean {
      return !!(this.meta && (this.meta.closed || this.meta.end <= Date.now()))
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
      if (!this.isAdmin) return false
      if (!this.meta) return true
      return !(this.meta.closed || this.meta.end <= Date.now())
    },
    voteCountForCurrent(): number {
      return this.selectedVersion ? this.versionVoteCounts[this.selectedVersion] || 0 : 0
    },
    formattedSubmitted(): string {
      return this.currentRulesSubmitted ? new Date(this.currentRulesSubmitted).toLocaleString() : ''
    },
    formattedStart(): string {
      return this.meta ? this.formatDate(this.meta.start) : ''
    },
    formattedEnd(): string {
      return this.meta ? this.formatDate(this.meta.end) : ''
    },
    currentAuthor(): string {
      return this.currentRulesAuthor
    },
    currentUsername() {
      return this.$store.state.auth.username
    }
  },
  watch: {
    selectedVersion(val) {
      const item = this.history.find(h => h.version === val)
      if (item) {
        this.fetchRules(item.id)
        this.loadRuleVotes()
      }
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
        author: g.createdBy,
        rule: g.rules[0] || ''
      }))
      await this.loadVersionVotes()
      if (this.history.length) {
        this.selectedVersion = this.history[0].version
        await this.fetchRules(this.history[0].id)
        this.loadRuleVotes()
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
      try {
        const m = JSON.parse(localStorage.getItem(key) || 'null')
        if (m && typeof m.closed !== 'undefined') {
          this.meta = m
          return
        }
      } catch {}
      this.meta = null
    },
    saveMeta() {
      const pid = Number(this.$route.params.id)
      const key = `annotation_rule_vote_meta_${pid}`
      localStorage.setItem(key, JSON.stringify(this.meta))
    },
    async loadVersionVotes() {
      const pid = Number(this.$route.params.id)
      const repo = new APIGridVoteRepository()
      const promises = this.history.map(h => repo.list(pid, h.id))
      const lists = await Promise.all(promises)
      const counts: Record<number, number> = {}
      const userArr: number[] = []
      lists.forEach((votes, idx) => {
        const ver = this.history[idx].version
        counts[ver] = votes.length
        if (votes.some((v: any) => v.user === this.currentUsername)) {
          userArr.push(ver)
        }
      })
      this.versionVoteCounts = counts
      this.userVotedVersions = userArr
    },
    async fetchRules(id: number) {
      this.rulesLoading = true
      try {
        const repo = new APIAnnotationRuleRepository()
        const grid = await repo.get(Number(this.$route.params.id), id)
        this.currentGridId = grid.id
        this.currentRules = grid.rules
        this.editRules = grid.rules.slice()
        this.currentRulesAuthor = grid.createdBy
        this.currentRulesSubmitted = grid.createdAt
        this.loadRuleVotes()
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
      this.editRules.push(t)
      this.newRule = ''
    },
    startEdit(idx: number) {
      this.newRule = this.editRules[idx]
      this.editRules.splice(idx, 1)
    },
    removeRule(idx: number) {
      this.editRules.splice(idx, 1)
    },
    scrollToAddInput() {
      this.$nextTick(() => {
        const el = document.getElementById('new-rule-input') as HTMLElement
        el?.focus()
      })
    },
    viewRule(rule: string, idx: number) {
      this.selectedRuleText = rule
      this.selectedRuleIndex = idx
      this.showRuleDialog = true
    },
    formatDate(ts: number): string {
      const d = new Date(ts)
      const day = String(d.getDate()).padStart(2, '0')
      const mon = String(d.getMonth() + 1).padStart(2, '0')
      const year = d.getFullYear()
      const hours = String(d.getHours()).padStart(2, '0')
      const mins = String(d.getMinutes()).padStart(2, '0')
      return `${day}/${mon}/${year} ${hours}:${mins}`
    },
    openEditDialog() {
      if (!this.meta) {
        const now = new Date()
        this.startDate = now.toISOString().slice(0, 10)
        this.startTime = now.toTimeString().slice(0, 5)
        const end = new Date(now.getTime() + 24 * 60 * 60 * 1000)
        this.endDate = end.toISOString().slice(0, 10)
        this.endTime = end.toTimeString().slice(0, 5)
        this.editStart = `${this.startDate} ${this.startTime}`
        this.editEnd = `${this.endDate} ${this.endTime}`
      } else {
        // init pickers from meta timestamps
        const s = new Date(this.meta.start)
        this.startDate = s.toISOString().slice(0,10)
        this.startTime = s.toTimeString().slice(0,5)
        this.editStart = `${this.startDate} ${this.startTime}`

        const e = new Date(this.meta.end)
        this.endDate = e.toISOString().slice(0,10)
        this.endTime = e.toTimeString().slice(0,5)
        this.editEnd = `${this.endDate} ${this.endTime}`
      }

      this.editDialog = true
    },
    saveEditPeriod() {
      if (!this.meta) {
        this.meta = { start: 0, end: 0, phase: 1, closed: false }
      }
      // parse back into timestamps
      const startTs = new Date(`${this.startDate}T${this.startTime}`).getTime()
      const endTs   = new Date(`${this.endDate}T${this.endTime}`).getTime()
      if (startTs && endTs) {
        this.meta.start = startTs
        this.meta.end   = endTs
        this.saveMeta()
      }
      this.editDialog = false
    },
    async saveRules() {
      if (!this.editRules.length) return
      this.savingRules = true
      try {
        const repo = new APIAnnotationRuleRepository()
        await repo.create(Number(this.$route.params.id), this.editRules)
        this.currentRules = this.editRules.slice()
        this.$router.push({
          path: '/message',
          query: {
            message: 'Rules updated!',
            redirect: `/projects/${this.$route.params.id}/voting`
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
      this.meta.closed = true
      this.saveMeta()
      const ver = this.$store.getters['projects/currentProject']?.versionNumber || this.selectedVersion
      this.$router.push({
        path: '/message',
        query: {
          message: `The Voting Period of the version ${ver} of the project has been closed`,
          redirect: `/projects/${this.$route.params.id}/voting`
        }
      })
    },
    async loadRuleVotes() {
      if (!this.currentGridId) return
      const repo = new APIRuleVoteRepository()
      const votes = await repo.list(Number(this.$route.params.id), this.currentGridId)
      const counts: Record<number, { up: number; down: number }> = {}
      const userMap: Record<number, string> = {}
      votes.forEach((v: any) => {
        if (!counts[v.rule_index]) counts[v.rule_index] = { up: 0, down: 0 }
        if (v.value === 'up') counts[v.rule_index].up++
        else counts[v.rule_index].down++
        if (v.user === this.currentUsername) userMap[v.rule_index] = v.value
      })
      this.ruleResults = counts
      this.userRuleVotes = userMap
      this.checkThreshold()
    },
    async voteRule(idx: number, val: string) {
      if (this.voteClosed) {
        this.$router.push({
          path: '/message',
          query: {
            message: 'This version of the project is now closed.',
            redirect: `/projects/${this.$route.params.id}/voting`
          }
        })
        return
      }
      if (this.userRuleVotes[idx]) return
      const repo = new APIRuleVoteRepository()
      await repo.create(Number(this.$route.params.id), {
        grid: this.currentGridId!,
        rule_index: idx,
        value: val
      })
      this.loadRuleVotes()
      const votedVer =
        this.$store.getters['projects/currentProject']?.versionNumber ||
        this.selectedVersion
      this.$router.push({
        path: '/message',
        query: {
          message: `Your vote on rule #${idx + 1} for version ${votedVer} has been registered!`,
          redirect: `/projects/${this.$route.params.id}/voting`
        }
      })
    },
    async submitVote() {
      if (this.voteClosed) {
        this.$router.push({
          path: '/message',
          query: {
            message: 'This version of the project is now closed.',
            redirect: `/projects/${this.$route.params.id}/voting`
          }
        })
        return
      }
      if (!this.selectedVersion) return
      this.saving = true
      const pid = Number(this.$route.params.id)
      const gridId = this.history.find(h => h.version === this.selectedVersion)?.id
      if (!gridId) {
        this.saving = false
        return
      }
      const repo = new APIGridVoteRepository()
      await repo.create(pid, { grid: gridId })
      await this.loadVersionVotes()
      this.saving = false

      const votedVer =
        this.$store.getters['projects/currentProject']?.versionNumber ||
        this.selectedVersion
      this.$router.push({
        path: '/message',
        query: {
          message: `Thank you for voting on version ${votedVer}!`,
          redirect: `/projects/${pid}/voting`
        }
      })
    },
    openResultsDialog() {
      // always open the in‐page results dialog
      this.showResultsDialog = true
    },
    applyStart() {
      this.editStart = `${this.startDate} ${this.startTime}`
      this.startMenu = false
    },
    applyEnd() {
      this.editEnd = `${this.endDate} ${this.endTime}`
      this.endMenu = false
    },
    checkThreshold() {
      if (!this.meta || this.meta.closed) return
      const entries = Object.entries(this.ruleResults)
      if (!entries.length) return
      const passed = entries.every(([_, v]) => {
        const total = v.up + v.down
        return total > 0 && v.up / total >= 0.8
      })
      if (passed) {
        this.meta.closed = true
        this.saveMeta()
      }
    }
  },
})
</script>

<style scoped>
.period-dates {
  font-size: 0.95rem;
  color: rgba(0,0,0,0.7);
}
</style>
