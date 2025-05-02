<template>
    <v-container fluid>
      <v-row class="mb-4" dense>
        <v-col
          v-for="tab in tabs"
          :key="tab.slug"
          cols="12" sm="6" md="3"
        >
          <v-btn block color="primary" @click="navigate(tab.slug)">
            {{ tab.label }}
          </v-btn>
        </v-col>
      </v-row>
  
      <v-divider class="my-4" />
  
      <!-- Aqui a sub‑view é renderizada -->
      <nuxt-child />
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { VContainer, VRow, VCol, VBtn, VDivider } from 'vuetify/lib'
  
  export default Vue.extend({
    name: 'ReportsIndex',
    layout: 'project',
    components: { VContainer, VRow, VCol, VBtn, VDivider },
    computed: {
      projectId(): string {
        return this.$route.params.id as string
      },
      tabs() {
        return [
          { slug: 'statistics',  label: 'Estatísticas' },
          { slug: 'history',     label: 'Histórico' },
          { slug: 'annotators',  label: 'Anotadores' },
          { slug: 'annotations', label: 'Anotações' }
        ]
      }
    },
    methods: {
      navigate(slug: string) {
        this.$router.push(
          `/projects/${this.projectId}/reports/${slug}`
        )
      }
    }
  })
  </script>
  
  <style scoped>
  /* Estilos se precisar */
  </style>