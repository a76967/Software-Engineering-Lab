<template>
  <v-container fluid>
    <v-card class="mx-auto my-6" max-width="800">
      <v-card-title>
        Voting on Annotation rules
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
            />
          </v-radio-group>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn
          color="primary"
          :disabled="!selectedVersion || saving"
          @click="submitVote"
        >
          Vote
        </v-btn>
      </v-card-actions>
    </v-card>
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

export default Vue.extend({
  layout: 'project',
  data() {
    return {
      history: [] as HistoryItem[],
      selectedVersion: null as number | null,
      loading: false,
      saving: false
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
    } catch (e) {
      console.error('Failed to fetch voting history', e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    submitVote() {
      this.saving = true
      console.log('Vote submitted for version', this.selectedVersion)
      this.$router.push({
        path: '/message',
        query: {
          message: `Thank you for voting on version ${this.selectedVersion}!`,
          redirect: `/projects/${this.$route.params.id}/annotation-rules`
        }
      })
    }
  }
})
</script>

<style scoped>
</style>