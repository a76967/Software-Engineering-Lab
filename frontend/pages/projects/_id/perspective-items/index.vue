<template>
  <v-container fluid class="pa-4">
    <v-card flat>
      <v-card-title>
        <span class="text-h5 font-weight-medium">Perspective Items</span>
        <v-spacer />
        <v-btn color="primary" @click="goToAdd" :disabled="selected.length > 0 || hasPerspectives">
          Add
        </v-btn>
        <v-btn
          color="error"
          class="ms-2"
          @click="removeSelected"
          :disabled="selected.length === 0 || hasPerspectives"
        >
          Delete
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-alert
          v-if="hasPerspectives"
          color="primary"
          dense
          class="mb-4 white--text"
        >
          At least 1 user perspective exists! Delete all to modify these items.
        </v-alert>
        <v-data-table
          :headers="headers"
          :items="allItems"
          item-key="name"
          show-select
          v-model="selected"
          :item-disabled="(item) => item.builtin || hasPerspectives"
          disable-pagination
          hide-default-footer
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #header.data-table-select>
            <v-simple-checkbox
              :indeterminate="selected.length > 0 && selected.length < selectableItems.length"
              :value="selected.length === selectableItems.length && selectableItems.length > 0"
              :disabled="selectableItems.length === 0 || hasPerspectives"
              @click.stop="(selectableItems.length === 0 ||
              hasPerspectives) ? null : toggleSelectAll()"
            />
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.data-table-select="{ item, isSelected, select }">
            <v-simple-checkbox
              :value="isSelected"
              @click.stop="(item.builtin || hasPerspectives)
              ? null : select(!isSelected)"
              :disabled="item.builtin || hasPerspectives"
              :class="{ 'builtin-checkbox': item.builtin,
              'perspective-disabled-checkbox': hasPerspectives && !item.builtin }"
            />
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.actions="{ item }">
            <v-btn
              icon
              small
              color="red"
              @click="removeItem(item)"
              :disabled="item.builtin || hasPerspectives"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.admin_perspective="{ item }">
            {{ perspectiveName(item.admin_perspective) }}
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.required="{ item }">
            <span class="required-icon" :class="item.required ? 'green' : 'red'">
              {{ item.required ? '✓' : '✗' }}
            </span>
          </template>
        </v-data-table>

        <!-- display current text‐allowed state -->
        <div class="mt-4">
          <strong>Text allowed?</strong>
          <span class="ms-2">{{ allowText ? 'Yes' : 'No' }}</span>
        </div>
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
      allowText: false,
      selected: [] as any[],
      items: [] as any[],
      builtinItems: [],
      adminPerspectives: [] as any[],
      hasPerspectives: false,
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Perspective', value: 'admin_perspective' },
        { text: 'Data Type', value: 'data_type' },
        { text: 'Required', value: 'required' },
        { text: '', value: 'actions', sortable: false }
      ],
      pendingItems: [] as any[],
      types: ['string', 'number', 'boolean', 'enum'],
      nameRules: [
        (v: string) => !!v || 'Name is required',
        (v: string) => {
          const s = this as any
          const dup = s.items.concat(s.pendingItems).some((it: any) => it.name === v)
          return !dup || 'Name duplicated'
        }
      ],
      dataTypeRules: [
        (v: string) => !!v || 'Data Type is required',
        (v: string) => {
          const s = this as any
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
      return this.allItems.filter((it) => !it.builtin)
    }
  },


  mounted() {
    this.fetchItems()
    this.fetchAdminPerspectives()
    const key = `allowText:${this.projectId}`
    this.allowText = localStorage.getItem(key) === 'true'
    this.checkPerspectives()
  },

  methods: {
    async checkPerspectives() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/perspectives/`, {
          params: { limit: 1 }
        })
        const data = res.data.results || res.data
        this.hasPerspectives = data.length > 0
      } catch {
        this.hasPerspectives = false
      }
    },
    toggleSelectAll() {
      if (this.selected.length === this.selectableItems.length) {
        this.selected = []
      } else {
        this.selected = [...this.selectableItems]
      }
    },

    async removeSelected() {
      if (this.hasPerspectives) return
      for (const it of this.selected) {
        await this.removeItem(it)
      }
      this.selected = []

      this.$router.push({
        path: this.localePath('/message'),
        query: {
          message: 'Perspective items deleted!',
          redirect: this.localePath(`/projects/${this.projectId}/perspective-items`)
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

    async fetchAdminPerspectives() {
      try {
        const res = await axios.get(`/v1/projects/${this.projectId}/admin-perspectives/`)
        this.adminPerspectives = res.data.results || res.data
      } catch {
        this.adminPerspectives = []
      }
    },

    perspectiveName(id: number | null): string {
      const p = this.adminPerspectives.find((ap: any) => ap.id === id)
      return p ? p.name : ''
    },

    goToAdd() {
      if (this.hasPerspectives) return
      this.$router.push(this.localePath(`/projects/${this.projectId}/perspective-items/add`))
    },

    async removeItem(item: any) {
      if (item.builtin || this.hasPerspectives) return
      await axios.delete(`/v1/projects/${this.projectId}/perspective-items/${item.id}/`)
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
.perspective-disabled-checkbox {
  pointer-events: none;
}
</style>