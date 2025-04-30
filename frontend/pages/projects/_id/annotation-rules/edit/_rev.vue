<template>
  <v-container fluid>
    <v-card class="mx-auto my-6" max-width="1200">
      <v-card-title>
        Edit Annotation Rules (v{{ rev }})
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
                @click="addRule"
                :disabled="!newRule.trim()"
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
              <v-hover v-slot="{ hover }">
                <div class="rule-cell" :class="{ empty: !r }">
                  <div class="action-texts" v-show="hover && i < rules.length">
                    <span class="action-link text--primary" @click.stop="startEdit(i)">
                      Edit
                    </span>
                    <span class="action-sep">|</span>
                    <span class="action-link text--error" @click.stop="deleteRule(i)">
                      Delete
                    </span>
                  </div>

                  <template v-if="editingIndex === i">
                    <v-text-field
                      v-model="editText"
                      dense solo hide-details
                      @keyup.enter="saveEdit(i)"
                      @blur="cancelEdit"
                    />
                  </template>
                  <template v-else>
                    <span v-if="r">{{ r }}</span>
                  </template>
                </div>
              </v-hover>
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
          @click="save"
          :loading="saving"
          :disabled="rules.length===0||saving"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { VHover } from 'vuetify/lib/components/VHover'
import { APIAnnotationRuleRepository } from '~/repositories/annotation-rule/apiAnnotationRuleRepository'

export default Vue.extend({
  layout: 'project',
  name: 'AnnotationRulesEditByRev',

  components: {
    VHover
  },

  data() {
    return {
      rules: [] as string[],
      newRule: '',
      loading: false,
      saving: false,
      editingIndex: null as number | null,
      editText: ''
    }
  },

  computed: {
    projectId(): number {
      return Number(this.$route.params.id)
    },
    rev(): number {
      return Number(this.$route.params.rev)
    },
    gridSize(): number {
      return Math.ceil(Math.sqrt(this.rules.length||1))
    },
    gridItems(): string[] {
      const total = this.gridSize * this.gridSize
      const arr = [...this.rules]
      while (arr.length < total) arr.push('')
      return arr
    }
  },

  async mounted() {
    this.loading = true
    try {
      const repo = new APIAnnotationRuleRepository()
      const grid = await repo.get(this.projectId, this.rev)
      this.rules = [...grid.rules]
    } catch (e) {
      console.error('Failed to load rules for editing', e)
    } finally {
      this.loading = false
    }
  },

  methods: {
    addRule() {
      const t = this.newRule.trim()
      if (!t) return
      this.rules.push(t)
      this.newRule = ''
    },
    async save() {
      if (!this.rules.length) return
      this.saving = true
      try {
        const repo = new APIAnnotationRuleRepository()
        await repo.create(this.projectId, this.rules)
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
    },
    startEdit(i: number) {
      this.editingIndex = i
      this.editText = this.rules[i]
    },
    cancelEdit() {
      this.editingIndex = null
      this.editText = ''
    },
    saveEdit(i: number) {
      if (!this.editText.trim()) return
      this.rules.splice(i, 1, this.editText.trim())
      this.cancelEdit()
    },
    deleteRule(i: number) {
      this.rules.splice(i, 1)
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