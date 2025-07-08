<template>
  <v-container fluid class="pa-0">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title v-if="isStaff">
            <v-btn class="text-capitalize" 
            color="primary" @click.stop="$router.push('projects/create')">
              {{ $t('generic.create') }}
            </v-btn>
            <v-btn class="text-capitalize ms-2" 
            color="primary" :disabled="!canClone" @click.stop="clone">
              Clone
            </v-btn>
            <v-btn
              class="text-capitalize ms-2"
              :disabled="!canDelete"
              outlined
              @click.stop="dialogDelete = true"
            >
              {{ $t('generic.delete') }}
            </v-btn>
            <v-dialog v-model="dialogDelete">
              <form-delete :selected="selected" @cancel="dialogDelete = false" @remove="remove" />
            </v-dialog>
          </v-card-title>
          <project-list
            :items="projects.items"
            :total="projects.count"
            :isLoading="isLoading"
            :value="selected"
            @update:query="updateQuery"
            @input="selected = $event"
          />
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import _ from 'lodash'
import { defineComponent } from 'vue'
import { mapGetters } from 'vuex'
import ProjectList from '@/components/project/ProjectList.vue'
import FormDelete from '~/components/project/FormDelete.vue'
import { Page } from '~/domain/models/page'
import { Project } from '~/domain/models/project/project'
import { SearchQueryData } from '~/services/application/project/projectApplicationService'

export default defineComponent({
  components: {
    FormDelete,
    ProjectList
  },
  layout: 'projects',

  middleware: ['check-auth', 'auth'],

  data() {
    return {
      dialogDelete: false,
      projects: {} as Page<Project>,
      selected: [] as Project[],
      isLoading: false
    }
  },

  async fetch() {
    this.isLoading = true
    this.projects = await this.$services.project.list(
      this.$route.query as unknown as SearchQueryData
    )
    this.isLoading = false
  },

  computed: {
    ...mapGetters('auth', ['isStaff']),
    canDelete(): boolean {
      return this.selected.length > 0
    },

    canClone(): boolean {
      return this.selected.length === 1
    }
  },

  watch: {
    '$route.query': _.debounce(function () {
      // @ts-ignore
      this.$fetch()
    }, 1000)
  },

  methods: {
    async remove() {
      await this.$services.project.bulkDelete(this.selected)
      this.$fetch()
      this.dialogDelete = false
      this.selected = []
    },

    async clone() {
      const project = await this.$services.project.clone(this.selected[0])
      this.selected = []
      this.$router.push(`/projects/${project.id}/settings`)
    },

    updateQuery(query: object) {
      this.$router.push(query)
    }
  }
})
</script>

<style scoped>
::v-deep .v-dialog {
  width: 800px;
}
</style>
