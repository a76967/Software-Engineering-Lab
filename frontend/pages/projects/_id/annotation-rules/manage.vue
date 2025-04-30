<template>
  <v-container fluid class="pa-0">
    <v-card class="mx-auto my-6" max-width="1200">
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
              color="primary"
              dark
              class="add-btn"
              @click="addRule"
              :disabled="!newRule.trim()"
            >
              Add new rule
            </v-btn>
          </v-col>
        </v-row>

        <div
          class="rules-grid"
          :style="{ gridTemplateColumns: `repeat(${gridSize}, 1fr)` }"
        >
          <div
            v-for="(cell, idx) in gridItems"
            :key="idx"
            :class="['rule-cell', { empty: !cell }]"
          >
            <span v-if="cell" class="rule-text">{{ cell }}</span>
          </div>
        </div>
      </v-card-text>

      <v-card-actions class="justify-center mt-4">
        <v-btn
          color="success"
          large
          @click="submitRules"
          :disabled="rules.length === 0"
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
  name: 'AnnotationRulesManage',

  data() {
    return {
      rules: [] as string[],
      newRule: '',
      isSubmitting: false
    }
  },

  computed: {
    gridSize(): number {
      return Math.ceil(Math.sqrt(this.rules.length || 1))
    },
    gridItems(): string[] {
      const total = this.gridSize * this.gridSize
      const items = [...this.rules]
      while (items.length < total) items.push('')
      return items
    }
  },

  methods: {
    addRule() {
      const txt = this.newRule.trim()
      if (!txt) return
      this.rules.push(txt)
      this.newRule = ''
    },

    async submitRules() {
      if (!this.rules.length) return
      this.isSubmitting = true
      try {
        const projectId = Number(this.$route.params.id)
        const repo = new APIAnnotationRuleRepository()
        await repo.create(projectId, this.rules)
        this.$router.push(`/projects/${projectId}/annotation-rules`)
      } catch (e) {
        console.error('Failed to submit rules', e)
      } finally {
        this.isSubmitting = false
      }
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
  border: 1px solid rgba(0, 0, 0, 0.12);
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

::v-deep .theme--dark .rule-cell {
  background-color: #424245 !important;
  border-color: rgba(255, 255, 255, 0.12) !important;
}

::v-deep .theme--dark .rule-cell.empty {
  background-color: #2e2e33 !important;
}

.add-btn {
  width: 100%;
}
</style>