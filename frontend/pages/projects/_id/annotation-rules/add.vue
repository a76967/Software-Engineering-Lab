<template>
  <v-container fluid>
    <v-card class="mx-auto my-6" max-width="1200">
      <v-alert
        v-if="error"
        type="error"
        dense
        class="mx-4 mt-4"
      >
        {{ error }}
      </v-alert>

      <v-card-title class="headline font-weight-medium">
        Annotation Rules
      </v-card-title>

      <v-card-text>
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
              :color="isAddDisabled ? 'grey lighten-1' : 'primary'"
              dark
              class="add-btn"
              @click="addRule"
              :disabled="isAddDisabled"
            >
              Add new rule
            </v-btn>
          </v-col>

          <v-col cols="12">
            <v-alert
              v-if="newRule.length > charLimit"
              type="error"
              dense
              text
            >
              Rule must be at most {{ charLimit }} characters.
            </v-alert>
          </v-col>
        </v-row>

        <!-- 1) Lista vertical -->
        <div class="rules-list">
          <div
            v-for="(cell, idx) in gridItems"
            :key="idx"
            :class="['rule-cell', { empty: !cell }]"
          >
            <span v-if="cell" class="rule-text">{{ cell }}</span>
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
          @click="submitRules"
          :loading="saving"
          :disabled="rules.length===0||saving"
        >
          Submit
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { APIAnnotationRuleRepository } from '~/repositories/annotation-rule/apiAnnotationRuleRepository'

export default Vue.extend({
  layout: 'project',
  name: 'AnnotationRulesAdd',

  data() {
    return {
      rules: [] as string[],
      newRule: '',
      saving: false,
      loading: false,
      charLimit: 25,
      error: ''
    }
  },

  computed: {
    projectId(): number {
      return Number(this.$route.params.id)
    },
    fromRev(): number {
      return Number(this.$route.query.from || 0)
    },
    gridItems(): (string|null)[] {
      return this.rules
    },
    gridSize(): number {
      return this.rules.length || 1
    },
    isAddDisabled(): boolean {
      return !this.newRule.trim() || this.newRule.length > this.charLimit
    }
  },

  async mounted() {
    if (this.fromRev) {
      this.loading = true
      try {
        const repo = new APIAnnotationRuleRepository()
        const grid = await repo.get(this.projectId, this.fromRev)
        this.rules = [...grid.rules]
      } catch (e) {
        console.error('Failed to load base grid', e)
      } finally {
        this.loading = false
      }
    }
  },

  methods: {
    addRule() {
      const txt = this.newRule.trim()
      if (!txt || txt.length > this.charLimit) return
      this.rules.unshift(txt)   // insere no início em vez do fim
      this.newRule = ''
    },

    async submitRules() {
      if (!this.rules.length) return
      this.saving = true
      this.error = '' // limpa erro anterior
      try {
        const repo = new APIAnnotationRuleRepository()
        await repo.create(this.projectId, this.rules)
        this.$router.push({
          path: '/message',
          query: {
            message: 'Rules added successfully!',
            redirect: `/projects/${this.projectId}/annotation-rules`
          }
        })
      } catch (e) {
        console.error('Failed to submit rules', e)
        this.error = "Error: Can't access our database!" // exibe no UI
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
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

/* mantém as regras visuais das células */
.rule-cell {
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 4px;
  padding: 12px;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
  transition: background-color 0.2s;
}
.rule-cell.empty {
  background-color: #e0e0e0;
}
.rule-text {
  font-size: 0.95rem;
  text-align: center;
  word-break: break-word;
}
</style>