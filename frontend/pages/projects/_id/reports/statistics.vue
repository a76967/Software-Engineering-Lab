<template>
    <v-container fluid>
      <h2>Estatísticas de Anotações</h2>
      <!-- Aqui vai o formulário de filtros + gráficos/tabelas -->
      <p>Filtros e visualizações de métricas aparecerão aqui.</p>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { VContainer } from 'vuetify/lib'
  
  export default Vue.extend({
    name: 'ReportsStatistics',
    layout: 'project',
    components: { VContainer },
    mounted() {
      console.log('Entrou em statistics.vue')
    }
  })
  </script>
  
  <style scoped>
  /* Ajustes visuais */
  </style>