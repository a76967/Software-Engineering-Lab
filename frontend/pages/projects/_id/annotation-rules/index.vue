<template>
    <v-container fluid class="pa-0">
      <v-card class="mx-auto my-6" max-width="1000">
        <v-card-title class="headline">
          Annotation Rules Overview
        </v-card-title>
  
        <v-card-text>
          <div>
            <h3>Current Submitted Grid</h3>
            <div v-if="!currentGrid.length" class="text--secondary">
              No grid has been submitted yet.
            </div>
            <div v-else class="rules-preview-grid">
              <div
                v-for="(cell, idx) in flattenedGrid"
                :key="idx"
                class="preview-cell"
              >
                {{ cell || '-' }}
              </div>
            </div>
          </div>
  
          <v-divider class="my-6"/>
  
          <div>
            <h3>History of Grids</h3>
            <v-simple-table v-if="history.length">
              <thead>
                <tr>
                  <th class="text-left">#</th>
                  <th class="text-left">Submitted At</th>
                  <th class="text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in history" :key="item.id">
                  <td>{{ item.id }}</td>
                  <td>{{ item.submittedAt }}</td>
                  <td>
                    <v-btn small text @click="viewHistory(item.id)">
                      View
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
          <v-btn color="primary" @click="goToManage">
            Manage Rules
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  
  interface HistoryItem {
    id: number
    submittedAt: string
  }
  
  export default Vue.extend({
    layout: 'project',
    name: 'AnnotationRulesIndex',
    data() {
      return {
        currentGrid: [
          ['Rule 1', 'Rule 2', 'Rule 3'],
          ['Rule 4', 'Rule 5', '']
        ] as string[][],
        history: [
          { id: 1, submittedAt: '2025-05-01 10:00' },
          { id: 2, submittedAt: '2025-05-03 14:30' }
        ] as HistoryItem[]
      }
    },
    computed: {
      // flatten grid into row-major order for preview cells
      flattenedGrid(): string[] {
        return this.currentGrid.reduce<string[]>(
          (acc, row) => acc.concat(row), []
        )
      },
      projectId(): number {
        return Number(this.$route.params.id)
      }
    },
    methods: {
      goToManage() {
        this.$router.push(
          `/projects/${this.projectId}/annotation-rules/manage`
        )
      },
      viewHistory(id: number) {
        // placeholder: navigate to a detailed view
        this.$router.push(
          `/projects/${this.projectId}/annotation-rules/manage?rev=${id}`
        )
      }
    }
  })
  </script>
  
  <style scoped>
  .rules-preview-grid {
    display: grid;
    grid-gap: 8px;
    margin-top: 8px;
    /* auto layout: 3 columns */
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