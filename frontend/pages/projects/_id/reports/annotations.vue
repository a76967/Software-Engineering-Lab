<template>
    <v-container fluid>
      <h2>Relatório de Anotações</h2>
      <!-- Aqui vai a UI do relatório -->
      <p>Formulário de filtros + tabela aparecerão aqui.</p>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { VContainer } from 'vuetify/lib'
  
  export default Vue.extend({
    name: 'ReportsAnnotations',
    layout: 'project',
    components: { VContainer },
    mounted() {
      console.log('Entrou em annotations.vue')
    }
  })
  </script>
  
  <style scoped>
  /* Ajustes visuais */
  </style>