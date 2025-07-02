<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title>
        <span class="text-h5 font-weight-medium">Perspective Items</span>
        <v-spacer />
        <v-btn
          color="primary"
          @click="goToAdd"
          :disabled="selected.length > 0"
        >
          Add
        </v-btn>
        <v-btn
          color="error"
          class="ms-2"
          @click="removeSelected"
          :disabled="selected.length === 0"
        >
          Delete
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="allItems"
          item-key="name"
          show-select
          v-model="selected"
          :item-disabled="item => item.builtin"
          disable-pagination
          hide-default-footer
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #header.data-table-select>
            <v-simple-checkbox
              :indeterminate="selected.length > 0 && selected.length < selectableItems.length"
              :value="selected.length === selectableItems.length && selectableItems.length > 0"
              :disabled="selectableItems.length === 0"
              @click.stop="toggleSelectAll"
            />
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.data-table-select="{ item, isSelected, select }">
            <v-simple-checkbox
              :value="isSelected"
              @click.stop="select(!isSelected)"
              :disabled="item.builtin"
              :class="{ 'builtin-checkbox': item.builtin }"
            />
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.actions="{ item }">
            <v-btn
              icon
              small
              color="red"
              @click="removeItem(item)"
              :disabled="item.builtin"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.required="{ item }">
            <span
              class="required-icon"
              :class="item.required ? 'green' : 'red'"
            >
              {{ item.required ? '✓' : '✗' }}
            </span>
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
  middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],

  data() {
    return {
      selected: [] as any[],
      items: [] as any[],
      builtinItems: [
        { name: 'Age', data_type: 'number', required: true, builtin: true },
        { name: 'Gender', data_type: 'string', required: true, builtin: true }
      ],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Data Type', value: 'data_type' },
        { text: 'Required', value: 'required' },
        { text: '', value: 'actions', sortable: false }
      ],
      pendingItems: [] as any[],
      types: ['string', 'number', 'boolean', 'enum'],
      nameRules: [
        (v: string) => !!v || 'Name is required',
        (v: string) => {
          const s = (this as any)
          const dup = s.items.concat(s.pendingItems)
            .some((it: any) => it.name === v)
          return !dup || 'Name duplicated'
        }
      ],
      dataTypeRules: [
        (v: string) => !!v || 'Data Type is required',
        (v: string) => {
          const s = (this as any)
          return s.types.includes(v) || 'Invalid Data Type'
        }
      ]
    }
  },

  computed: {
    projectId(): number {
      return Number(this.$route.params.id)
    },
    allItems(): any[] {
      return [...this.builtinItems, ...this.items]
    },
    selectableItems(): any[] {
      return this.allItems.filter(it => !it.builtin)
    }
  },

  mounted() {
    this.fetchItems()
  },

  methods: {
    toggleSelectAll() {
      if (this.selected.length === this.selectableItems.length) {
        this.selected = []
      } else {
        this.selected = [...this.selectableItems]
      }
    },

    async removeSelected() {
      for (const it of this.selected) {
        await this.removeItem(it)
      }
      this.selected = []

      this.$router.push({
        path: this.localePath('/message'),
        query: {
          message: 'Perspective items deleted!',
          redirect: this.localePath(
            `/projects/${this.projectId}/perspective-items`
          )
        }
      })
    },

    async fetchItems() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/perspective-items/`)
        this.items = (res.data.results || res.data).map((it: any) => ({
          ...it,
          builtin: false
        }))
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
    }
  }
})
</script>

<style scoped>
.v-data-table__actions {
  width: 72px;
}

.required-icon {
  font-weight: 700;
  font-size: 1.3rem;
  line-height: 1;
  display: inline;
  padding: 0;
  background: transparent !important;
  border: none !important;
  transition: color 0.3s ease;
}
.required-icon.green {
  color: #4caf50;
}
.required-icon.red {
  color: #f44336;
}
.builtin-checkbox {
  pointer-events: none;
}
</style>