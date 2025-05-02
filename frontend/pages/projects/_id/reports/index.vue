<template>
  <v-container fluid>
    <!-- Header with description -->
    <v-sheet color="primary lighten-5" class="pa-6 mb-8" rounded>
      <h1 class="display-1 mb-2">Reports</h1>
      <p class="subtitle-1">
        Select the type of report you want to generate for this project.
      </p>
    </v-sheet>

    <!-- Grid of cards -->
    <v-row dense>
      <v-col
        v-for="tab in tabs"
        :key="tab.slug"
        cols="12" sm="6" md="3"
      >
        <v-hover v-slot="{ hover }">
          <v-card
            :elevation="hover ? 8 : 2"
            class="pa-6 text-center cursor-pointer"
            @click="navigate(tab.slug)"
          >
            <v-icon size="48" color="primary">
              {{ tab.icon }}
            </v-icon>
            <h3 class="headline mt-4">{{ tab.label }}</h3>
            <p class="text--secondary">{{ tab.desc }}</p>
          </v-card>
        </v-hover>
      </v-col>
    </v-row>

    <v-divider class="my-8" />

    <!-- Render selected sub-view here -->
    <nuxt-child />
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import {
  VContainer, VSheet, VRow, VCol, VCard,
  VIcon, VDivider, VHover
} from 'vuetify/lib'
import {
  mdiChartBar,
  mdiHistory,
  mdiAccountGroup,
  mdiTable
} from '@mdi/js'

export default Vue.extend({
  name: 'ReportsIndex',
  components: {
    VContainer, VSheet, VRow, VCol,
    VCard, VIcon, VDivider, VHover
  },
  layout: 'project',
  computed: {
    projectId(): string {
      return this.$route.params.id as string
    },
    tabs(): Array<{ slug: string; label: string; desc: string; icon: string }> {
      return [
        { slug: 'statistics', label: 'Statistics', desc: 'Metrics and charts for annotations', icon: mdiChartBar },
        { slug: 'history',     label: 'History',     desc: 'Previous versions and timestamps', icon: mdiHistory },
        { slug: 'annotators',  label: 'Annotators',  desc: 'User performance metrics',         icon: mdiAccountGroup },
        { slug: 'annotations', label: 'Annotations', desc: 'Detailed list with filters',        icon: mdiTable }
      ]
    }
  },
  methods: {
    navigate(slug: string) {
      this.$router.push(`/projects/${this.projectId}/reports/${slug}`)
    }
  }
})
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
</style>