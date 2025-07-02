<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title>
        <span class="text-h5 font-weight-medium">Admin Perspectives</span>
        <v-spacer/>
        <v-btn color="primary" @click="goToAdd" :disabled="selected.length > 0">
          Add
        </v-btn>
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

export default Vue.extend({
  layout: 'project',

  data() {
    return {
      items: [] as any[],
      selected: [] as any[],
      headers: [
        { text: 'Subject',   value: 'subject' },
        { text: 'Category',  value: 'category' },
        { text: 'User',      value: 'user' },
        { text: 'Actions',   value: 'actions', sortable: false }
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
    canEdit(): boolean {
      return this.selected.length === 1
    }
  },

  mounted() {
    this.fetchItems()
  },

  methods: {
    async fetchItems() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/perspectives/`)
        this.items = res.data.results || res.data
      } catch {
        this.items = []
      }
    },

    goToAdd() {
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
        `/v1/projects/${this.projectId}/perspectives/${item.id}/`
      )
      this.fetchItems()
    },

    async removeSelected() {
      this.isDeleting = true
      await Promise.all(
        this.selected.map(it =>
          axios.delete(`/v1/projects/${this.projectId}/perspectives/${it.id}/`)
        )
      )
      this.isDeleting = false
      this.dialogDelete = false
      this.selected = []
      this.fetchItems()
    }
  }
})
</script>

<style scoped>
/* add custom styles here if needed */
</style>