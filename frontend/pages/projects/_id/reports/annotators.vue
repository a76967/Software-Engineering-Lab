<template>
    <v-container fluid>
      <h2>Relatório de Anotadores</h2>
      <!-- Aqui vai o formulário de filtros + estatísticas por anotador -->
      <p>Filtros e métricas de performance por usuário aparecerão aqui.</p>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { VContainer } from 'vuetify/lib'
  
  export default Vue.extend({
    name: 'ReportsAnnotators',
    layout: 'project',
    components: { VContainer },
    mounted() {
      console.log('Entrou em annotators.vue')
    }
  })
  </script>
  
  <style scoped>
  /* Ajustes visuais */
  </style>