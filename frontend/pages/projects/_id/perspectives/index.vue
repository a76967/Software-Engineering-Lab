<template>
  <div>
    <v-card>
      <v-card-title>
        <v-btn color="primary" class="text-capitalize ms-2" @click="goToAdd">
          {{ $t('generic.add') }}
        </v-btn>
        <v-btn
          class="text-capitalize ms-2"
          :disabled="!canEdit || !canDeletePerspective(selected[0])"
          outlined
          @click="editPerspective"
        >
          Edit
        </v-btn>
        <v-btn
          class="text-capitalize ms-2"
          :disabled="!canDelete"
          outlined
          @click.stop="requestDelete"
        >
          {{ $t('generic.delete') }}
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-text-field
          v-model="search"
          :prepend-inner-icon="icons.mdiMagnify"
          :label="$t('generic.search')"
          single-line
          hide-details
          filled
          style="margin-bottom: 1rem"
        />

        <v-progress-circular
          v-if="isLoading"
          class="ma-3"
          indeterminate
          color="primary"
        />

        <v-alert v-if="dbError" type="error" dense>
          {{ dbError }}
        </v-alert>

        <div v-if="!isLoading && !dbError" class="d-flex justify-center">
          <div style="max-width: 800px; width: 100%;">
            <div
              v-for="(item) in filteredItems"
              :key="item.id"
              class="mb-4 d-flex align-center"
            >
              <v-checkbox
                v-model="selected"
                :value="item"
                hide-details
                class="mr-2"
                :ripple="false"
                :disabled="selected.length > 0 && !isSelected(item) && !canDeletePerspective(item)"
              />
              <v-card
                class="flex-grow-1"
                outlined
                elevation="2"
                rounded
                :class="{
                  'selected-card': isSelected(item),
                  'disabled-card': selected.length > 0 && !canDeletePerspective(item)
                }"
              >
                <v-sheet
                  :color="item.user.role === 'project_admin' ? 'orange' : 'primary'"
                  dark
                  class="py-3 px-4 rounded-t-lg d-flex flex-column"
                >
                  <div class="text-h6 font-weight-medium">
                    {{ item.user.username }}'s perspective
                  </div>
                  <div class="text-body-2">
                    {{ formatTime(item.created_at) }}
                    <span v-if="item.updated_at !== item.created_at">
                      &bull; Updated: {{ formatTime(item.updated_at) }}
                    </span>
                  </div>
                </v-sheet>

                <v-card-text>
                  <div v-html="formatPerspectiveText(item.text, item.id)"></div>
                  <div
                    v-if="item.linkedAnnotations && item.linkedAnnotations.length"
                  >
                    <v-divider class="my-2" />
                    <div
                      v-for="ann in item.linkedAnnotations"
                      :key="ann.uniqueId"
                      class="d-flex align-center"
                    >
                      <span
                        v-if="ann.text"
                        style="cursor: pointer;"
                        @click="viewAnnotation(item, ann)"
                      >
                        <strong>Annotation:</strong>
                        {{ ann.text }}
                        <span v-if="ann.label">
                          ({{ ann.label }})
                        </span>
                        <span v-if="ann.linkedBy">
                          — linked by <strong>{{ ann.linkedBy }}</strong>
                        </span>
                      </span>
                      <v-spacer />
                      <v-btn
                        icon
                        small
                        color="primary"
                        :disabled="!canEditAnnotation(item, ann)"
                        @click="editAnnotation(item, ann)"
                      >
                        <v-icon>{{ icons.mdiPencil }}</v-icon>
                      </v-btn>
                      <v-btn
                        icon
                        small
                        color="red"
                        :disabled="!canDeleteAnnotation(item, ann)"
                        @click="removeAnnotation(item, ann)"
                      >
                        <v-icon>{{ icons.mdiTrashCan }}</v-icon>
                      </v-btn>
                    </div>
                  </div>
                </v-card-text>

              </v-card>
            </div>

            <div v-if="items.length === 0">
              <p>No perspectives available.</p>
            </div>
          </div>
        </div>
      </v-card-text>

      <v-dialog v-model="dialogLink" persistent max-width="600px">
        <v-card>
          <v-card-title>
            Select a Dataset item to link its annotations
          </v-card-title>
          <v-card-text>
            <v-alert v-if="annotationFetchError" type="error" dense>
              {{ annotationFetchError }}
            </v-alert>
            <v-select
              v-model="selectedDataset"
              :items="datasetItems"
              :item-text="getDatasetLabel"
              item-value="id"
              label="Choose a dataset item"
              :item-disabled="isItemDisabled"
              :disabled="!!annotationFetchError"
              dense
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn
              color="secondary"
              text
              @click="confirmLink"
              :disabled="!!annotationFetchError"
            >
              Confirm
            </v-btn>
            <v-btn text @click="closeLinkDialog">
              Cancel
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <delete-dialog
        v-model="dialogDelete"
        :dbError="dbError"
        :deleteDialogText="deleteDialogText"
        :isDeleting="isDeleting"
        @confirm-delete="removePerspective"
        @cancel-delete="closeDeleteDialog"
      />
    </v-card>

    <v-dialog v-model="showDuplicateDialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">Warning</v-card-title>
        <v-card-text>
          You can’t create more than 1 perspective per user! Edit or delete yours first!
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text color="primary" @click="showDuplicateDialog = false">
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <info-dialog v-model="showInfoDialog" :message="infoDialogMessage" />
  </div>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'
import { DataOptions } from 'vuetify/types'
import { mapGetters } from 'vuex'
import { mdiMagnify, mdiPencil, mdiTrashCan } from '@mdi/js'
import { getLinkToAnnotationPage } from '~/presenter/linkToAnnotationPage'
import DeleteDialog from '~/pages/projects/_id/perspectives/delete.vue'
import InfoDialog from '~/components/utils/InfoDialog.vue'

export default Vue.extend({
  name: 'PerspectivesTable',
  layout: 'project',
  components: {
    DeleteDialog,
    InfoDialog
  },
  data() {
    return {
      dialogDelete: false,
      dialogLink: false,
      selectedDataset: null,
      datasetItems: [] as any[],
      annotationFetchError: "",
      currentPerspective: null as any,
      selected: [] as any[],
      search: '',
      filters: {
        category: ''
      },
      options: {
        page: 1,
        itemsPerPage: 10,
        sortBy: ['created_at'],
        sortDesc: [true]
      } as DataOptions,
      items: [] as any[],
      total: 0,
      isLoading: false,
      categoryTypes: [] as Array<{ text: string; value: string }>,
      dbError: '',
      showDuplicateDialog: false,
      showInfoDialog: false,
      infoDialogMessage: '',
      isDeleting: false,
      icons: {
        mdiMagnify,
        mdiPencil,
        mdiTrashCan
      },
      nameRules: [
        (v: string) => !!v || 'Name is required',
        (v: string) => {
          const exists =
            this.items.some(it => it.name === v) ||
            this.pendingItems.some(it => it.name === v)
          return !exists || 'Name duplicated'
        }
      ],
      dataTypeRules: [
        (v: string) => !!v || 'Data Type is required',
        (v: string) => this.types.includes(v) || 'Invalid Data Type'
      ]
    }
  },
  computed: {
    ...mapGetters('projects', ['project']),
    ...mapGetters('auth', ['getUsername', 'getRolename']),
    user() {
      return {
        username: this.getUsername || 'Unknown',
        role: this.getRolename || 'annotator'
      }
    },
    isProjectAdmin(): boolean {
      return (this.user.role || '').toLowerCase() === 'project_admin'
    },
    deletablePerspectives(): any[] {
      return this.items.filter((item: any) => item.user.username === this.user.username)
    },
    canEdit(): boolean {
      return this.selected.length === 1
    },
    canDelete(): boolean {
      if (!this.selected.length) return false
      return this.selected.every(item => this.canDeletePerspective(item))
    },
    deleteDialogText(): string {
      return this.selected.length > 1
        ? "Are you sure you want to delete these perspectives?"
        : "Are you sure you want to delete this perspective?"
    },
    filteredItems(): any[] {
      const term = this.search.trim().toLowerCase()
      if (!term) return this.items
      return this.items.filter(item => {
        const user  = item.user.username?.toLowerCase() || ''
        const subj  = (item.subject || '').toLowerCase()
        const text  = (item.text    || '').toLowerCase()
        const cat  = (item.category || '').toLowerCase()
        return user.includes(term)
            || subj.includes(term)
            || text.includes(term)
            || cat.includes(term)
      })
    }
  },
  watch: {
    options: {
      handler() {
        this.updateQuery()
      },
      deep: true
    },
    search() {
    },
    'filters.category'() {
      this.options.page = 1
      this.updateQuery()
    },
    // Reload perspectives when returning to this page
    '$route'(to, from) {
      if (to.fullPath !== from.fullPath) {
        this.fetchPerspectives()
      }
    }
  },
  mounted() {
    this.fetchPerspectives()
    this.fetchCategoryTypes()
  },
  methods: {
    goToAdd() {
      if (this.items.some(item => item.user.username === this.user.username)) {
        this.showDuplicateDialog = true
        return
      }
      const projectId = this.$route.params.id
      this.$router.push(
        this.localePath(`/projects/${projectId}/perspectives/add`)
      )
    },
    editPerspective() {
    if (!this.canEdit) {
      console.error("Select exactly one perspective to edit!")
      return
    }
    const projectId = this.$route.params.id
    const perspective = this.selected[0]
    if (perspective.linkedAnnotations && perspective.linkedAnnotations.length) {
      this.infoDialogMessage = 'You already have annotations associated with the perspective'
      this.showInfoDialog = true
      return
    }
    this.$router.push(
      this.localePath(
        `/projects/${projectId}/perspectives/edit?perspectiveId=${perspective.id}`
      )
    )
  },
  closeDeleteDialog() {
    this.dialogDelete = false
  },
  canDeletePerspective(item: any): boolean {
    return item.user.username === this.user.username
  },
  requestDelete() {
    if (!this.canDelete) return
    const hasAnn = this.selected.some(it => it.linkedAnnotations && it.linkedAnnotations.length)
    if (hasAnn) {
      this.infoDialogMessage = 'You already have annotations associated with the perspective'
      this.showInfoDialog = true
      return
    }
    this.dialogDelete = true
  },
  removePerspective() {
    if (!this.canDelete) {
      console.error("No permission to delete selected perspectives.")
      return
      }
      const projectId = this.$route.params.id
      this.isDeleting = true
      const deletable = this.selected
        .filter(item => this.canDeletePerspective(item))
      const deletePromises = deletable.map((perspective: any) =>
        axios.delete(`/v1/projects/${projectId}/perspectives/${perspective.id}/`)
      )
      Promise.all(deletePromises)
        .then(() => {
          deletable.forEach((p: any) => this.clearPerspectiveColors(p.id))
          this.fetchPerspectives()
          this.dialogDelete = false
          this.selected = []
          this.$router.push({
            path: '/message',
            query: {
              message: 'Perspectives deleted successfully!',
              redirect: `/projects/${projectId}/perspectives`
            }
          })
        })
        .catch((error: any) => {
          console.error("Error deleting perspectives:", error.response || error.message)
          this.dbError = "Can't access our database!"
        })
        .finally(() => {
          this.isDeleting = false
        })
    },
    fetchPerspectives() {
      const projectId = this.$route.params.id
      const query: any = {
        limit: this.options.itemsPerPage,
        offset: ((this.options.page ? this.options.page - 1 : 0) *
          this.options.itemsPerPage)
      }
      if (this.filters.category) query.category = this.filters.category
      this.isLoading = true
      this.dbError = ''
      axios.get(`/v1/projects/${projectId}/perspectives/`, { params: query })
        .then((_response: any) => {
          const data = _response.data
          const items = data.results || []
          const promises = items.map((item: any) => {
            if (typeof item.user === 'number') {
              return axios.get(`/v1/users/${item.user}/`)
                .then((_userResponse: any) => {
                  item.user = _userResponse.data
                })
                .catch(() => {
                  item.user = { username: 'N/A' }
                })
            }
            return Promise.resolve()
          })
          Promise.all(promises).then(() => {
            this.items = items
            this.total = data.count || items.length
          })
        })
        .catch((error: any) => {
          console.error(
            'Error fetching perspectives:',
            error.response || error.message
          )
          this.dbError = "Can't access our database!"
          this.items = []
        })
        .finally(() => {
          this.isLoading = false
        })
    },
    updateQuery() {
      this.fetchPerspectives()
    },
    timeAgo(dateStr: string): string {
      if (!dateStr) return 'N/A'
      const cleanDateStr = dateStr
        .replace(' ', 'T')
        .replace(/(\.\d{3})\d+/, '$1')
        .replace(/([+-]\d{2})(\d{2})$/, '$1:$2')
      const dateObj = new Date(cleanDateStr)
      if (isNaN(dateObj.getTime())) return 'N/A'
      const now = new Date()
      const diffMs = now.getTime() - dateObj.getTime()
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
    formatTime(time: string): string {
      return this.timeAgo(time)
    },
    openLinkDialog(perspective: any) {
      this.currentPerspective = perspective
      this.dialogLink = true
      this.annotationFetchError = ""
      this.fetchDatasetItems()
    },
    fetchDatasetItems() {
      axios
        .get(`/v1/projects/${this.$route.params.id}/examples?limit=10&offset=0`)
        .then((_response: any) => {
          this.datasetItems = _response.data.results || []
          this.annotationFetchError = ""
        })
        .catch((error: any) => {
          console.error('Error fetching dataset items:', error.response || error.message)
          this.annotationFetchError = "Error: Can't access our database!"
          this.selectedDataset = null
        })
    },
    fetchCategoryTypes() {
      const projectId = this.$route.params.id
      axios.get(`/v1/projects/${projectId}/category-types/`)
        .then((_response: any) => {
          this.categoryTypes =
            _response.data.results || _response.data || []
        })
        .catch((error: any) => {
          console.error(
            'Error fetching category types:',
            error.response || error.message
          )
        })
    },
    confirmLink() {
      if (!this.selectedDataset || !this.currentPerspective) {
        console.error('selectedDataset or currentPerspective is not set.')
        return
      }
      const datasetItem = this.datasetItems.find(
        item => item.id === this.selectedDataset
      )
      if (!datasetItem) {
        console.error('Dataset item not found.')
        return
      }
      const truncatedText = datasetItem.text.length > 50
        ? datasetItem.text.substring(0, 50) + '...'
        : datasetItem.text
      let label = ''
      let categoryId = null
      let fullCategory = null
      if (datasetItem.category && this.categoryTypes.length > 0) {
        let category
        if (typeof datasetItem.category === 'object') {
          category = this.categoryTypes.find(
            (cat: any) => String(cat.id) === String(datasetItem.category.id)
          )
        } else {
          category = this.categoryTypes.find(
            (cat: any) => String(cat.id) === String(datasetItem.category)
          )
        }
        if (category) {
          label = category.text
          categoryId = category.id
          fullCategory = { ...category }
        }
      }
      const annotation = {
        id: datasetItem.id,
        uniqueId: `${datasetItem.id}-${Date.now()}`,
        text: truncatedText,
        label,
        categoryId,
        category: fullCategory,
        linkedBy: this.user.username,
        linkedByRole: this.user.role
      }
      this.items.forEach((item: any, index: number) => {
        if (item.id === this.currentPerspective.id) {
          const duplicate = item.linkedAnnotations &&
            item.linkedAnnotations.find(
              (ann: any) => ann.id === datasetItem.id
            )
          if (duplicate) {
            console.warn(`Annotation for dataset item ${datasetItem.id} is already linked.`)
            return
          }
          const updatedAnnotations = item.linkedAnnotations
            ? [...item.linkedAnnotations, annotation]
            : [annotation]
          this.$set(this.items, index, {
            ...item,
            linkedAnnotations: updatedAnnotations
          })
          const projectId = this.$route.params.id
          axios.patch(
            `/v1/projects/${projectId}/perspectives/${this.currentPerspective.id}/`,
            { linkedAnnotations: updatedAnnotations }
          )
            .then((_response: any) => {
              this.fetchPerspectives()
              this.closeLinkDialog()
              this.$router.push({
                path: '/message',
                query: {
                  message: 'Annotation linked successfully!',
                  redirect: `/projects/${projectId}/perspectives`
                }
              })
            })
            .catch((error: any) => {
              console.error("Error updating perspective:", error.response || error.message)
            })
        }
      })
    },
    closeLinkDialog() {
      this.dialogLink = false
      this.selectedDataset = null
      this.currentPerspective = null
    },
    getDatasetLabel(item: any): string {
      const snippet = item.text
        ? item.text.substring(0, 50) + (item.text.length > 50 ? '...' : '')
        : ''
      const timeLabel = item.created_at
        ? this.formatTime(item.created_at)
        : item.upload_name || 'Unknown time'
      return `${snippet} (${timeLabel})`
    },
    isItemDisabled(item: any) {
      if (!this.currentPerspective || !this.currentPerspective.linkedAnnotations) {
        return false
      }
      return this.currentPerspective.linkedAnnotations.some(
        (ann: any) => ann.id === item.id
      )
    },
    canEditAnnotation(perspective: any, ann: any): boolean {
      const role   = this.user.role
      const author = perspective.user.username
      const by     = ann.linkedBy
      const byRole = ann.linkedByRole || 'annotator'
      if (role === 'annotator') {
        return author === this.user.username && by === this.user.username
      }
      if (role === 'project_admin') {
        return byRole !== 'project_admin'
      }
      return false
    },
    canDeleteAnnotation(perspective: any, ann: any): boolean {
      const role = this.user.role
      const author = perspective.user.username
      const byRole = ann.linkedByRole || 'annotator'
      if (role === 'annotator') {
        return author === this.user.username && byRole === 'annotator'
      }
      if (role === 'project_admin') {
        return byRole !== 'project_admin'
      }
      return false
    },
    removeAnnotation(item: any, ann: any) {
      if (!this.canDeleteAnnotation(item, ann)) {
        console.error("No permission to delete this annotation.")
        return
      }
      const updated = item.linkedAnnotations.filter((a: any) => a.uniqueId !== ann.uniqueId)
      const idx = this.items.findIndex((it: any) => it.id === item.id)
      this.$set(this.items, idx, { ...item, linkedAnnotations: updated })
      axios.patch(
        `/v1/projects/${this.$route.params.id}/perspectives/${item.id}/`,
        { linkedAnnotations: updated }
      )
        .then(() => this.fetchPerspectives())
        .catch(err => console.error(err))
    },
    editAnnotation(item: any, ann: any) {
      if (!this.canEditAnnotation(item, ann)) {
        console.error("No permission to edit this annotation.")
        return
      }
      const projectId = this.$route.params.id
      const found = item.linkedAnnotations.findIndex((a: any) => a.uniqueId === ann.uniqueId)
      const page = (found !== -1 ? found : 0) + 1
      const link = getLinkToAnnotationPage(projectId, this.project.projectType)
      this.$router.push({
        path: this.localePath(link),
        query: { page: page.toString() }
      })
    },
    viewAnnotation(item: any, ann: any) {
      const projectId = this.$route.params.id
      const limit = 10
      let index = 0
      if (item.linkedAnnotations && item.linkedAnnotations.length) {
        const found = item.linkedAnnotations.findIndex(
          (a: any) => a.uniqueId === ann.uniqueId
        )
        index = found !== -1 ? found : 0
      }
      const offset = index * limit
      this.$router.push({
        path: this.localePath(`/projects/${projectId}/dataset`),
        query: {
          limit: limit.toString(),
          offset: offset.toString()
        }
      })
    },
    getPerspectiveLabel(perspective: any): string {
      return perspective.subject || perspective.text || 'Perspective'
    },
    selectPerspective(item: any) {
      if (this.isSelected(item)) {
        this.selected = []
      } else {
        this.selected = [item]
      }
    },
    isSelected(item: any): boolean {
      return this.selected.length === 1 && this.selected[0].id === item.id
    },
    getUserPerspectiveIndex(item: any): number {
      const userItems = this.filteredItems
        .filter(i => i.user.username === item.user.username)
      const pos = userItems.findIndex(i => i.id === item.id)
      return pos >= 0 ? pos + 1 : 0
    },
    colorFromString(str: string): string {
      let hash = 0
      for (let i = 0; i < str.length; i++) {
        hash = (hash << 5) - hash + str.charCodeAt(i)
        hash |= 0
      }
      const r = Math.abs(hash) % 156 + 100
      const g = Math.abs((hash >> 8)) % 156 + 100
      const b = Math.abs((hash >> 16)) % 156 + 100
      return '#' + [r, g, b]
        .map(c => c.toString(16).padStart(2, '0'))
        .join('')
        .toUpperCase()
    },
    randomHexColor(): string {
      const r = Math.floor(Math.random() * 156 + 100)
      const g = Math.floor(Math.random() * 156 + 100)
      const b = Math.floor(Math.random() * 156 + 100)
      return '#' + [r, g, b]
        .map(c => c.toString(16).padStart(2, '0'))
        .join('')
        .toUpperCase()
    },
    getSegmentColor(id: number, seg: string): string {
      const key = `persp-color-${id}-${seg}`
      let color = localStorage.getItem(key) || ''
      if (!color) {
        color = this.items.length > 1
          ? this.randomHexColor()
          : this.colorFromString(seg)
        localStorage.setItem(key, color)
      }
      return color
    },
    clearPerspectiveColors(id: number) {
      const prefix = `persp-color-${id}-`
      for (let i = localStorage.length - 1; i >= 0; i--) {
        const k = localStorage.key(i) || ''
        if (k.startsWith(prefix)) {
          localStorage.removeItem(k)
        }
      }
    },
    formatPerspectiveText (text: string = '', id?: number): string {
      const dot = text.indexOf('. ')

      const metaStr =
        dot === -1 ? text.trim() : text.slice(0, dot).trim()
      const rest = dot === -1 ? '' : text.slice(dot + 2).trim()

      const segments = metaStr.split(',').map(s => s.trim()).map(seg => {
        const [key, ...valParts] = seg.split(':')
        let val = valParts.join(':').trim()
        if (val.toLowerCase() === 'true')  val = 'Yes'
        if (val.toLowerCase() === 'false') val = 'No'
        const color = id ? this.getSegmentColor(id, seg) : this.colorFromString(seg)
        const textColor = this.$contrastColor(color)
        return `<span class="persp-meta" style="background-color:${color};color:${textColor};">${key}: ${val}</span>`
      })

      return `
        <div>${segments.join(' ')}</div>
        ${rest ? `<div>${rest}</div>` : ''}
      `
    }
  }
})
</script>

<style scoped>
.selected-card {
  border: 2px solid #1976D2;
}
.disabled-card {
  opacity: 0.5;
  pointer-events: none;
}

::v-deep .persp-meta {
  font-weight: bold;
  display: inline-block;
  padding: 2px 6px;
  border-radius: 8px;
  margin-right: 4px;
}
</style>