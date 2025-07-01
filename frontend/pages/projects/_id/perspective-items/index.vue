<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title>
        <span class="text-h5 font-weight-medium">Perspective Items</span>
        <v-spacer/>
        <v-btn color="primary" @click="goToAdd">
          Add
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="allItems"
          dense
          disable-pagination
          hide-default-footer
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.actions="{ item }">
            <v-btn icon small color="red"
                   @click="removeItem(item)"
                   :disabled="item.builtin">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import axios from 'axios'

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth','auth','setCurrentProject','isProjectAdmin'],

  data() {
    return {
      items: [] as any[],
      builtinItems: [
        { name:'Age',    data_type:'number',  required:true,  builtin:true },
        { name:'Gender', data_type:'string',  required:true,  builtin:true }
      ],
      headers: [
        { text:'Name',      value:'name'      },
        { text:'Data Type', value:'data_type' },
        { text:'Required',  value:'required'  },
        { text:'',          value:'actions', sortable:false }
      ]
    }
  },

  computed: {
    projectId(): number {
      return Number(this.$route.params.id)
    },
    allItems(): any[] {
      return [...this.builtinItems, ...this.items]
    }
  },

  mounted() {
    this.fetchItems()
  },

  methods: {
    async fetchItems() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/perspective-items/`)
        this.items = (res.data.results || res.data).map((it: any) => ({ ...it, builtin:false }))
      } catch {
        this.items = []
      }
    },

    goToAdd() {
      this.$router.push(
        this.localePath(`/projects/${this.projectId}/perspective-items/add`)
      )
    },

    async removeItem(item: any) {
      if (item.builtin) return
      await axios.delete(
        `/v1/projects/${this.projectId}/perspective-items/${item.id}/`
      )
      this.fetchItems()
    }
  }
})
</script>

<style scoped>
.v-data-table__actions {
  width: 72px;
}
</style>