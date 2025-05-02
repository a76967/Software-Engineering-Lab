<template>
    <v-container fluid class="pa-0">
      <v-card class="mx-auto my-6" max-width="1200">
        <v-card-title class="headline font-weight-medium">
            Annotation Rules overview
        </v-card-title>
  
        <v-card-text>
          <div>
            <p v-if="isViewingLatest">
              The current rules for the project are the following:
              (v{{ currentVersion }}):
            </p>
            <p v-else>
              Viewing archived rules (v{{ currentVersion }}):
            </p>
            <div v-if="loading" class="text--secondary">Loading…</div>
            <div v-else-if="!currentRules.length" class="text--secondary">
              No rules submitted yet.
            </div>
            <div v-else class="rules-preview-grid">
              <div
                v-for="(cell, idx) in currentRules"
                :key="idx"
                class="preview-cell"
              >
                {{ cell || '-' }}
              </div>
            </div>
          </div>
  
          <v-divider class="my-6"/>
  
          <div>
            <h3>History of chosen rules</h3>
            <v-simple-table v-if="history.length">
              <thead>
                <tr>
                  <th class="text-left">#</th>
                  <th class="text-left">Author</th>
                  <th class="text-left">Submitted</th>
                  <th class="text-left">View</th>
                  <th class="text-left">Edit</th>
                  <th class="text-left">Delete</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in history" :key="item.id">
                  <td>{{ item.version }}</td>
                  <td>{{ item.author }}</td>
                  <td>{{ timeAgo(item.createdAt) }}</td>
                  <td>
                    <v-btn small text @click="showVersion(item.id)">
                      View
                    </v-btn>
                  </td>
                  <td>
                    <v-btn small text color="primary" @click="goToEdit(item.id)">
                      Edit
                    </v-btn>
                  </td>
                  <td>
                    <v-btn small text color="error"
                      :disabled="item.author !== currentUsername"
                      @click="showDeleteDialog(item.id, item.version)">
                      Delete
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </v-simple-table>
            <div v-else class="text--secondary">
              No history yet.
            </div>
          </div>
        </v-card-text>
  
        <v-card-actions>
          <v-spacer/>
          <v-btn color="primary" @click="goToAdd">
            Add new Rules
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-dialog v-model="deleteDialog" max-width="400">
        <v-card>
          <v-card-title class="headline">
            Delete Rules?
          </v-card-title>
          <v-card-text>
            Are you sure you want to delete version {{ deleteTargetVersion }}?
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
            <v-btn text @click="cancelDelete">Cancel</v-btn>
            <v-btn text color="error" @click="confirmDelete">
              Yes, Delete
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script lang="ts">
  /* eslint-disable */
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
            authorId: g.createdBy
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
  
      showVersion(id: number) {
        const selected = this.history.find(h => h.id === id)
        const grid = selected && this.history.length
          ? this.history.map(h => h).find(h => h.id === id)
          : null
        if (grid) {
          const repo = new APIAnnotationRuleRepository()
          repo.get(this.projectId, id).then(g => {
            this.currentRules = g.rules
            this.currentVersion = g.version
          }).catch(err => {
            console.error('Failed to load selected grid', err)
          })
        }
      },
  
      timeAgo(dateStr: string): string {
        const then = new Date(dateStr.replace(' ', 'T')).getTime()
        const now = Date.now()
        const diff = Math.floor((now - then) / 1000)
        if (diff < 60) return `${diff}s ago`
        const mins = Math.floor(diff / 60)
        if (mins < 60) return `${mins}m ago`
        const hrs = Math.floor(mins / 60)
        if (hrs < 24) return `${hrs}h ago`
        const days = Math.floor(hrs / 24)
        return `${days}d ago`
      },
  
      goToAdd() {
        this.$router.push(`/projects/${this.projectId}/annotation-rules/add`)
      },

      goToEdit(rev: number) {
        this.$router.push(
          `/projects/${this.projectId}/annotation-rules/edit/${rev}`
        )
      },

      showDeleteDialog(id: number, version: number) {
        this.deleteTargetId = id
        this.deleteTargetVersion = version
        this.deleteDialog = true
      },

      cancelDelete() {
        this.deleteDialog = false
        this.deleteTargetId = null
      },

      async confirmDelete() {
        if (!this.deleteTargetId) return
        this.deleteDialog = false
        try {
          const repo = new APIAnnotationRuleRepository()
          await repo.delete(this.projectId, this.deleteTargetId)
          this.$router.push({
            path: '/message',
            query: {
              message: 'Rules deleted successfully!',
              redirect: `/projects/${this.projectId}/annotation-rules`
            }
          })
        } catch (e) {
          console.error('Delete failed', e)
        } finally {
          this.deleteTargetId = null
        }
      }
    }
  })
  </script>
  
  <style scoped>
  .rules-preview-grid {
    display: grid;
    grid-gap: 8px;
    margin-top: 8px;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  .preview-cell {
    border: 1px solid rgba(0,0,0,0.12);
    border-radius: 4px;
    padding: 12px;
    text-align: center;
    background-color: #fafafa;
  }
  .theme--dark .preview-cell {
    background-color: #424245;
    border-color: rgba(255,255,255,0.12);
    color: #e0e0e0;
  }
  </style>