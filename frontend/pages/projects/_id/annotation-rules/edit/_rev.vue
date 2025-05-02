<template>
  <v-container fluid>
    <v-card class="mx-auto my-6" max-width="1200">
      <v-card-title>
        Annotation Rules
      </v-card-title>
      <v-card-text>
        <div v-if="loading" class="text--secondary">Loading…</div>
        <div v-else>
          <v-row align="center" class="mb-6" no-gutters>
            <v-col cols="12" md="9">
              <v-text-field
                v-model="newRule"
                placeholder="Add your new annotation rule here…"
                dense
                outlined
                hide-details
                @keyup.enter="addRule"
              />
            </v-col>
            <v-col cols="12" md="3" class="text-right">
              <v-btn
                color="primary"
                class="add-btn white--text"
                :disabled="!newRule.trim()"
                @click="addRule"
              >
                Add new rule
              </v-btn>
            </v-col>
          </v-row>

          <div
            class="rules-grid"
            :style="{ gridTemplateColumns: `repeat(${gridSize},1fr)` }"
          >
            <div v-for="(r, i) in gridItems" :key="i">
              <div class="rule-cell" :class="{ empty: !r }">
                <span v-if="r">{{ r }}</span>
              </div>
            </div>
          </div>
        </div>
      </v-card-text>

      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="goBack">
          Cancel
        </v-btn>
        <v-btn
          color="success"
          :loading="saving"
          :disabled="rules.length===0||saving"
          @click="save"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import { mapGetters } from 'vuex'
import { APIAnnotationRuleRepository } from '~/repositories/annotation-rule/apiAnnotationRuleRepository'

interface HistoryItem {
  id: number
  version: number
  author: string
  createdAt: string
  authorId: number
}

export default Vue.extend({
  name: 'AnnotationRulesIndex',
  layout: 'project',

  data() {
    return {
      loading: false as boolean,
      currentRules: [] as string[],
      newRule: '' as string,
      saving: false as boolean,
      currentVersion: 0 as number,
      history: [] as HistoryItem[],
      deleteDialog: false as boolean,
      deleteTargetId: null as number | null,
      deleteTargetVersion: 0 as number
    }
  },

  computed: {
    projectId(): number {
      return Number(this.$route.params.id)
    },
    isViewingLatest(): boolean {
      return (
        this.history.length > 0 &&
        this.currentVersion === this.history[0].version
      )
    },
    rules(): string[] {
      return this.currentRules
    },
    gridItems(): (string|null)[] {
      return this.currentRules
    },
    gridSize(): number {
      return this.currentRules.length || 1
    },
    ...mapGetters('auth', {
      currentUserId: 'getUserId',
      currentUsername: 'getUsername'
    })
  },

  async mounted() {
    await this.fetchGrids()
  },

  methods: {
    async fetchGrids() {
      this.loading = true
      try {
        const repo = new APIAnnotationRuleRepository()
        const grids = await repo.list(this.projectId)
        grids.sort((a, b) => b.version - a.version)
        this.history = grids.map(g => ({
          id: g.id,
          version: g.version,
          author: g.createdBy,
          createdAt: g.createdAt,
          authorId: Number(g.createdBy)
        }))
        if (grids.length) {
          this.currentRules = grids[0].rules
          this.currentVersion = grids[0].version
        }
      } catch (e) {
        console.error('Failed to load annotation grids', e)
      } finally {
        this.loading = false
      }
    },

    addRule() {
      const t = this.newRule.trim()
      if (!t) return
      this.currentRules.push(t)
      this.newRule = ''
    },
    async save() {
      if (!this.currentRules.length) return
      this.saving = true
      try {
        const repo = new APIAnnotationRuleRepository()
        await repo.create(this.projectId, this.currentRules)
        this.$router.push({
          path: '/message',
          query: {
            message: 'New rules version created!',
            redirect: `/projects/${this.projectId}/annotation-rules`
          }
        })
      } catch (e) {
        console.error('Failed to create new grid', e)
      } finally {
        this.saving = false
      }
    },
    goBack() {
      this.$router.push(`/projects/${this.projectId}/annotation-rules`)
    }
  }
})
</script>

<style scoped>
.rules-grid {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}
.rule-cell {
  position: relative;
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 4px;
  padding: 12px;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}
.rule-cell.empty {
  background-color: #e0e0e0;
}
.action-texts {
  position: absolute;
  top: 4px; right: 4px;
}
.opacity-hidden { opacity: 0; }
.rule-cell:hover .action-texts { opacity: 1; }

.action-link {
  cursor: pointer;
  font-size: 0.75rem;
  user-select: none;
}
.action-sep {
  margin: 0 4px;
  color: rgba(0,0,0,0.54);
  font-size: 0.75rem;
}

.action-link.text--primary {
  color: #6376AB !important;
}
.action-link.text--error {
  color: rgb(225, 35, 35) !important;
}

::v-deep .theme--dark .rule-cell {
  background-color: #424245 !important;
  border-color: rgba(255,255,255,0.12) !important;
  color: #e0e0e0 !important;
}
::v-deep .theme--dark .rule-cell.empty {
  background-color: #2e2e33 !important;
}

.add-btn {
  width: 100%;
  margin-left: 0.5vw;
}
</style>