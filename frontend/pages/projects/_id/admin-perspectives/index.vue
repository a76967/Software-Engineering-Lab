<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title>
        <span class="text-h5 font-weight-medium">Admin Perspectives</span>
        <v-spacer/>
        <v-btn color="primary" @click="goToAdd" :disabled="!canAdd">Add</v-btn>
        <v-btn
          class="ms-2"
          outlined
          @click="editItem"
          :disabled="!canEdit"
        >
          Edit
        </v-btn>
        <v-btn
          class="ms-2"
          color="error"
          outlined
          @click="dialogDelete = true"
          :disabled="!selected.length"
        >
          Delete
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="items"
          item-key="id"
          show-select
          v-model="selected"
          disable-pagination
          hide-default-footer
          class="elevation-1"
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.subject="{ item }">
            {{ item.subject }}
          </template>
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.category="{ item }">
            {{ item.category }}
          </template>
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.user="{ item }">
            {{ item.user.username }}
          </template>
          <!-- format Created At -->
          <template #[`item.created_at`]="{ item }">
            <span>{{ timeAgo(item.created_at) }}</span>
          </template>
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.actions="{ item }">
            <v-btn icon small color="red" @click="removeOne(item)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>

      <delete-dialog
        v-model="dialogDelete"
        deleteDialogText="Delete selected perspectives?"
        :isDeleting="isDeleting"
        @confirm-delete="removeSelected"
        @cancel-delete="dialogDelete = false"
      />
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import axios from 'axios'
import DeleteDialog from '~/pages/projects/_id/admin-perspectives/delete.vue'

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],
  components: {
    DeleteDialog
  },

  data() {
    return {
      items: [] as any[],
      selected: [] as any[],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Description', value: 'description' },
        { text: 'Created At', value: 'created_at' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      dialogDelete: false,
      isDeleting: false,
      dbError: ''
    }
  },

  computed: {
    projectId(): number {
      return Number(this.$route.params.id)
    },
    userId(): number {
      return this.$store.state.auth.id
    },
    canEdit(): boolean {
      return this.selected.length === 1
    },
    canAdd(): boolean {
      return !this.items.some(it => it.user === this.userId)
    }
  },

  mounted() {
    this.fetchItems()
  },

  methods: {
    async fetchItems() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/admin-perspectives/`)
        this.items = res.data.results || res.data
      } catch {
        this.items = []
      }
    },

    goToAdd() {
      if (!this.canAdd) return
      this.$router.push(this.localePath(
        `/projects/${this.projectId}/admin-perspectives/add`
      ))
    },

    editItem() {
      if (!this.canEdit) return
      const id = this.selected[0].id
      this.$router.push(this.localePath(
        `/projects/${this.projectId}/admin-perspectives/edit?perspectiveId=${id}`
      ))
    },

    async removeOne(item: any) {
      await axios.delete(
        `/v1/projects/${this.projectId}/admin-perspectives/${item.id}/`
      )
      this.fetchItems()
    },

    async removeSelected() {
      this.isDeleting = true
      await Promise.all(
        this.selected.map(it =>
          axios.delete(`/v1/projects/${this.projectId}/admin-perspectives/${it.id}/`)
        )
      )
      this.isDeleting = false
      this.dialogDelete = false
      this.selected = []
      this.fetchItems()
    },

    timeAgo(dateStr: string): string {
      if (!dateStr) return ''
      const now = new Date()
      const past = new Date(dateStr)
      const diffMs = now.getTime() - past.getTime()
      const diffSeconds = Math.floor(diffMs / 1000)
      if (diffSeconds < 60) return `${diffSeconds} seconds ago`
      const diffMinutes = Math.floor(diffSeconds / 60)
      if (diffMinutes < 60) return `${diffMinutes} minutes ago`
      const diffHours = Math.floor(diffMinutes / 60)
      if (diffHours < 24) return `${diffHours} hours ago`
      const diffDays = Math.floor(diffHours / 24)
      if (diffDays < 30) return `${diffDays} days ago`
      const diffMonths = Math.floor(diffDays / 30)
      if (diffMonths < 12) return `${diffMonths} months ago`
      const diffYears = Math.floor(diffMonths / 12)
      return `${diffYears} years ago`
    }
  }
})
</script>

<style scoped>
/* add custom styles here if needed */
</style>