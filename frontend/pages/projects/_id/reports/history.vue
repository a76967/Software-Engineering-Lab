<template>
    <v-container fluid>
      <h2>Histórico de Anotações</h2>
      <!-- Aqui vai o formulário de filtros + tabela de histórico -->
      <p>Filtros e tabela de versões anteriores aparecerão aqui.</p>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { VContainer } from 'vuetify/lib'
  
  export default Vue.extend({
    name: 'ReportsHistory',
    layout: 'project',
    components: { VContainer },
    mounted() {
      console.log('Entrou em history.vue')
    }
  })
  </script>
  
  <style scoped>
  /* Ajustes visuais */
  </style>