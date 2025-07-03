<!-- eslint-disable vue/valid-v-slot -->
<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title>
        <span class="text-h5 font-weight-medium">Admin Perspectives</span>
        <v-spacer />
        <v-btn :disabled="!canAdd" color="primary" @click="goToAdd">Add</v-btn>
        <v-btn
          :disabled="!canEdit"
          class="ms-2"
          outlined
          @click="editItem"
        >
          Edit
        </v-btn>
        <v-btn
          :disabled="!selected.length"
          class="ms-2"
          color="error"
          outlined
          @click="dialogDelete = true"
        >
          Delete
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="items"
          item-key="id"
          show-select
          disable-pagination
          hide-default-footer
          class="elevation-1"
        >
          <!-- render the child items column -->
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.items="{ item }">
            <ul class="ps-2 mb-0">
              <li
                v-for="(f, i) in item.fields.slice(0, 3)"
                :key="i"
                class="small"
              >
                {{ f.name }} ({{ f.data_type }})
              </li>
              <li v-if="item.fields.length > 3" class="small">…</li>
            </ul>
          </template>
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
          <template #item.created_at="{ item }">
            <span>{{ timeAgo(item.created_at) }}</span>
          </template>
          <!-- Actions column slot -->
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.actions="{ item }">
            <v-btn text small color="primary" @click="openViewDialog(item)">
              VIEW
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>

      <!-- View-items dialog -->
      <v-dialog v-model="viewDialog" max-width="400px">
        <v-card>
          <v-card-title>Items of {{ currentView.name }}</v-card-title>
          <v-card-text>
            <ul>
              <li v-for="(f,i) in currentView.fields" :key="i">
                {{ f.name }} ({{ f.data_type }})
              </li>
            </ul>
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
            <v-btn text @click="viewDialog = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <delete-dialog
        v-model="dialogDelete"
        :delete-dialog-text="deleteDialogText"
        :is-deleting="isDeleting"
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
  components: {
    DeleteDialog
  },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],

  data() {
    return {
      items: [] as any[],
      selected: [] as any[],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Description', value: 'description' },
        { text: 'Created At', value: 'created_at' },
        { text: 'Items', value: 'items', sortable: false },
        { text: 'Created By', value: 'user', sortable: false },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      dialogDelete: false,
      isDeleting: false,
      deleteDialogText:
        'Delete selected perspectives?\nBy deleting this perspective, all its items and user perspectives will also be deleted.',
      dbError: '',
      // view dialog state
      viewDialog: false,
      currentView: {} as any
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
      return this.items.length === 0
    }
  },

  mounted() {
    this.fetchItems()
  },

  methods: {
    async fetchItems() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/admin-perspectives/`)
        const list = res.data.results || res.data

        // fetch child perspective-items for each perspective
        const withFields = await Promise.all(
          list.map(async (p: any) => {
            try {
              const r = await axios.get(
                `/v1/projects/${this.projectId}/perspective-items/`,
                { params: { admin_perspective: p.id } }
              )
              p.fields = r.data.results || r.data
            } catch {
              p.fields = []
            }
            return p
          })
        )

        this.items = withFields
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

    editItem(id?: number) {
      const pid = this.projectId
      const perspectiveId = id ?? (this.selected[0] && this.selected[0].id)
      if (!perspectiveId) return
      this.$router.push(
        this.localePath(`/projects/${pid}/admin-perspectives/edit?perspectiveId=${perspectiveId}`)
      )
    },

    async removeOne(item: any) {
      await axios.delete(
        `/v1/projects/${this.projectId}/admin-perspectives/${item.id}/`
      )
      this.fetchItems()
      this.$router.push({
        path: this.localePath('/message'),
        query: {
          message: 'Admin perspective deleted successfully!',
          redirect: this.localePath(
            `/projects/${this.projectId}/admin-perspectives`
          )
        }
      })
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
      this.$router.push({
        path: this.localePath('/message'),
        query: {
          message: 'Admin perspectives deleted successfully!',
          redirect: this.localePath(
            `/projects/${this.projectId}/admin-perspectives`
          )
        }
      })
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
    },

    openViewDialog(item: any) {
      this.currentView = item
      this.viewDialog = true
    }
  }
})
</script>

<style scoped>
/* add custom styles here if needed */
</style>
