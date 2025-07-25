<template>
    <v-app id="inspire">
      <v-main>
        <v-container fluid class="pa-4">
          <v-row align="center" justify="center" class="mt-5">
            <v-col cols="12" sm="10" md="8">
              <v-card class="pa-0 overflow-hidden rounded-lg shadow-lg">
                <v-sheet color="primary" class="py-4 px-6 rounded-t-lg">
                  <div class="text-h6 font-weight-medium" style="color: white">Edit Users</div>
                </v-sheet>
                <v-card-text class="pa-4">
                  <v-alert v-if="errorMessage" type="error" dismissible class="mb-4">
                    {{ errorMessage }}
                  </v-alert>
                  <v-text-field
                    v-model="search"
                    :prepend-inner-icon="mdiMagnify"
                    label="Search"
                    single-line
                    hide-details
                    filled
                    class="mb-4"
                  />
                  <v-data-table
                    :headers="headers"
                    :items="pagedUsers"
                    :items-per-page="options.itemsPerPage"
                    item-key="id"
                    :loading="isLoading"
                    loading-text="Loading users..."
                    :item-class="getRowClass"
                    :options.sync="options"
                    :custom-sort="customSort"
                    hide-default-footer
                  >
                    <template #[`item.id`]="{ item }">
                      <span v-if="!item._empty">{{ item.id }}</span>
                      <span v-else>&nbsp;</span>
                    </template>
                    <template #[`item.username`]="{ item }">
                      <div v-if="!item._empty" class="d-flex align-center">
                        <span
                          class="status-circle"
                          :style="{ backgroundColor: getStatusColor(item) }"
                        ></span>
                        <span>{{ item.username }}</span>
                      </div>
                      <span v-else>&nbsp;</span>
                    </template>
                    <template #[`item.email`]="{ item }">
                      <span v-if="!item._empty">{{ item.email }}</span>
                      <span v-else>&nbsp;</span>
                    </template>
                    <template #[`item.role`]="{ item }">
                      <v-chip
                        v-if="!item._empty"
                        :color="
                          item.role === 'owner'
                            ? '#a8c400'
                            : item.role === 'admin'
                            ? '#FF2F00'
                            : 'primary'
                        "
                        outlined
                      >
                        {{ item.role.charAt(0).toUpperCase() + item.role.slice(1) }}
                      </v-chip>
                      <div v-else>&nbsp;</div>
                    </template>
                    <template #[`item.date_joined`]="{ item }">
                      <span v-if="!item._empty">{{ timeAgo(item.date_joined) }}</span>
                      <span v-else>&nbsp;</span>
                    </template>
                    <template #[`item.last_seen`]="{ item }">
                      <span v-if="!item._empty">
                        {{
                          isCurrentUser(item)
                            ? 'Currently online'
                            : item.last_login
                            ? timeAgo(item.last_login)
                            : 'Never'
                        }}
                      </span>
                      <span v-else>&nbsp;</span>
                    </template>
                    <template #[`item.actions`]="{ item }">
                      <v-btn
                        v-if="!item._empty"
                        icon
                        color="primary"
                        :disabled="!canEdit(item)"
                        @click="openEdit(item)"
                      >
                        <v-icon>{{ mdiPencil }}</v-icon>
                      </v-btn>
                      <span v-else>&nbsp;</span>
                    </template>
                    <template #footer>
                      <v-row align="center">
                        <v-col class="d-flex justify-start">
                          <v-btn color="primary" @click="$router.push('/list-user')">
                            <v-icon left>{{ mdiChevronLeft }}</v-icon>
                            Back
                          </v-btn>
                        </v-col>
                        <v-col class="d-flex justify-end">
                          <v-pagination
                            v-model="options.page"
                            :length="Math.ceil(sortedUsers.length / options.itemsPerPage)"
                            total-visible="7"
                          />
                        </v-col>
                      </v-row>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          <v-dialog v-model="editDialog" max-width="500px">
            <v-card>
              <v-sheet color="primary" class="py-4 px-6 rounded-t-lg">
                <div class="text-h6" style="color: white">
                  Edit User: {{ editingUser.username || 'User' }}
                </div>
              </v-sheet>
              <v-card-text class="pa-4">
                <v-alert v-if="editErrorMessage" type="error" dismissible class="mb-4">
                  {{ editErrorMessage }}
                </v-alert>
                <v-form ref="editForm">
                  <v-text-field
                    v-model="editingUser.username"
                    label="Username"
                    outlined
                    :prepend-icon="mdiAccount"
                  ></v-text-field>
                  <v-text-field
                    v-model="editingUser.email"
                    label="Email"
                    outlined
                    :prepend-icon="mdiEmail"
                  ></v-text-field>
                  <v-select
                    v-model="editingUser.role"
                    :items="roleOptions"
                    label="Role"
                    outlined
                    :prepend-icon="mdiAccountKey"
                    :color="selectedRoleColor"
                  ></v-select>
                </v-form>
              </v-card-text>
              <v-card-actions>
                <v-btn color="primary" @click="saveEdit">Save</v-btn>
                <v-btn text @click="closeEdit">Cancel</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-container>
      </v-main>
    </v-app>
  </template>
  
  <script>
  import { mdiMagnify, mdiChevronLeft, mdiPencil, mdiAccount, mdiEmail, mdiAccountKey } from '@mdi/js'
  import { mapState } from 'vuex'
  
  export default {
    data() {
      return {
        users: [],
        search: '',
        isLoading: false,
        errorMessage: '',
        editErrorMessage: '',
        options: {
          itemsPerPage: 5,
          page: 1,
          sortBy: [],
          sortDesc: []
        },
        headers: [
          { text: 'Username', value: 'username', sortable: true },
          { text: 'Email', value: 'email', sortable: true },
          { text: 'Role', value: 'role', sortable: true },
          { text: 'Joined', value: 'date_joined', sortable: true },
          { text: 'Last Seen', value: 'last_seen', sortable: true },
          { text: 'Actions', value: 'actions', sortable: false }
        ],
        mdiMagnify,
        mdiChevronLeft,
        mdiPencil,
        mdiAccount,
        mdiEmail,
        mdiAccountKey,
        editDialog: false,
        editingUser: {},
        originalEditingUser: {}
      }
    },
    computed: {
      ...mapState('auth', {
        id: (state) => state.id,
        isStaff: (state) => state.isStaff,
        is_superuser: (state) => state.is_superuser
      }),
      currentUser() {
        return {
          id: this.id,
          role:
            this.is_superuser && this.isStaff
              ? 'owner'
              : !this.is_superuser && this.isStaff
              ? 'admin'
              : 'annotator'
        }
      },
      currentUserId() {
        return this.currentUser.id
      },
      currentUserRole() {
        return this.currentUser.role
      },
      roleOptions() {
        const options = [
          { text: 'Annotator', value: 'annotator', disabled: false },
          { text: 'Admin', value: 'admin', disabled: false },
          { text: 'Owner', value: 'owner', disabled: false }
        ]
  
        if (this.currentUserRole === 'annotator') {
          options.find((opt) => opt.value === 'admin').disabled = true
          options.find((opt) => opt.value === 'owner').disabled = true
        } else if (this.currentUserRole === 'admin') {
          options.find((opt) => opt.value === 'owner').disabled = true
        }
  
        return options
      },
      selectedRoleColor() {
        if (this.editingUser && this.editingUser.role) {
          if (this.editingUser.role === 'admin') {
            return '#FF2F00'
          } else if (this.editingUser.role === 'owner') {
            return '#a8c400'
          }
        }
        return 'primary'
      },
      sortedUsers() {
        const lowerSearch = this.search.toLowerCase()
        const usersWithRole = this.users.map((user) => ({
          ...user,
          role: user.role
            ? user.role
            : user.is_staff && !user.is_superuser
            ? 'admin'
            : user.is_superuser && user.is_staff
            ? 'owner'
            : 'annotator'
        }))
        const filtered = usersWithRole.filter(
          (user) =>
            user.username.toLowerCase().includes(lowerSearch) ||
            user.email.toLowerCase().includes(lowerSearch)
        )
        return this.customSort(filtered, this.options.sortBy, this.options.sortDesc)
      },
      pagedUsers() {
        const start = (this.options.page - 1) * this.options.itemsPerPage
        const end = start + this.options.itemsPerPage
        const pageItems = this.sortedUsers.slice(start, end)
        while (pageItems.length < this.options.itemsPerPage) {
          pageItems.push({ _empty: true })
        }
        return pageItems
      }
    },
    watch: {
      search() {
        this.options.page = 1
        this.fetchUsers()
      }
    },
    async created() {
      await this.fetchUsers()
      console.log(this.$store.state.auth)
    },
    methods: {
      async fetchUsers() {
        this.isLoading = true
        try {
          const response = await this.$axios.get('/v1/users/')
          this.users = response.data
          this.errorMessage = ''
        } catch (error) {
          if (error.response && error.response.data) {
            const data = error.response.data
            if (typeof data === 'string' && data.trim().startsWith('<')) {
              this.errorMessage = "Error: Can't access our database!"
            } else {
              const errors = []
              for (const [field, messages] of Object.entries(data)) {
                const formattedMessages = Array.isArray(messages) ? messages.join(', ') : messages
                errors.push(
                  `${field.charAt(0).toUpperCase() + field.slice(1)}: ${formattedMessages.replace(
                    /^\n+/,
                    ''
                  )}`
                )
              }
              this.errorMessage = errors.join('\n\n')
            }
          } else {
            this.errorMessage = 'Error fetching users'
          }
          console.error('Error fetching users:', error)
        } finally {
          this.isLoading = false
        }
      },
      getRowClass(item) {
        return item._empty ? 'dummy-row' : ''
      },
      canEdit(user) {
        if (user.id === this.currentUserId) return true
        if (this.currentUserRole === 'owner') {
          return user.role !== 'owner'
        }
        if (this.currentUserRole === 'admin') {
          return user.role === 'annotator'
        }
        return false
      },
      openEdit(item) {
        this.editErrorMessage = ''
        this.originalEditingUser = JSON.parse(JSON.stringify(item))
        this.editingUser = { ...item }
        this.editDialog = true
      },
      async saveEdit() {
        try {
          if (this.editingUser.role === 'owner') {
            this.editingUser.is_superuser = true
            this.editingUser.is_staff = true
          } else if (this.editingUser.role === 'admin') {
            if (this.currentUserRole === 'annotator') {
              this.editingUser.is_superuser = false
              this.editingUser.is_staff = false
              this.editingUser.role = 'annotator'
            } else {
              this.editingUser.is_superuser = false
              this.editingUser.is_staff = true
              this.editingUser.role = 'admin'
            }
          } else {
            this.editingUser.is_superuser = false
            this.editingUser.is_staff = false
            this.editingUser.role = 'annotator'
          }
          let response
          if (this.editingUser.id) {
            response = await this.$axios.put(`/v1/users/${this.editingUser.id}/`, this.editingUser)
            const index = this.users.findIndex((u) => u.id === this.editingUser.id)
            if (index !== -1) {
              this.$set(this.users, index, response.data)
            }
  
            if (this.editingUser.id === this.currentUserId) {
              this.$store.commit('auth/updateUser', {
                id: response.data.id,
                username: response.data.username,
                is_staff: response.data.is_staff,
                is_superuser: response.data.is_superuser
              })
            }
          } else {
            response = await this.$axios.post('/v1/users/', this.editingUser)
            this.users.push(response.data)
          }
          this.options.page = 1
          this.editDialog = false
          this.$router.push({
            path: '/message',
            query: {
              message: 'User updated successfully!',
              redirect: '/edit-user'
            }
          })
        } catch (error) {
          console.error('Error saving user:', error)
          this.editingUser = { ...this.originalEditingUser }
          let errorDetail = ''
          if (error.response && error.response.data) {
            const data = error.response.data
            if (data.username) {
              errorDetail = "Error: " + (Array.isArray(data.username) ? data.username.join(' ') : data.username)
            } else if (data.email) {
              errorDetail = (Array.isArray(data.email) ? data.email.join(' ') : data.email)
            } else if (typeof data === 'string' && data.trim().startsWith('<')) {
              errorDetail = "Error: Can't access our database!"
            } else {
              const errors = []
              for (const [field, messages] of Object.entries(data)) {
                const formattedMessages =
                  Array.isArray(messages) ? messages.join(' ') : messages
                errors.push(
                  `${field.charAt(0).toUpperCase() + field.slice(1)}: ${formattedMessages.replace(/^\n+/, '')}`
                )
              }
              errorDetail = errors.join('\n')
            }
          } else {
            errorDetail = 'Error saving user'
          }
          this.editErrorMessage = errorDetail
          console.error('Error details:', error.response && error.response.data)
        }
      },
      closeEdit() {
        this.editDialog = false
        this.editErrorMessage = ''
      },
      isCurrentUser(user) {
        return user.id === this.currentUserId
      },
      getStatusColor(user) {
        return this.isCurrentUser(user) ? 'green' : 'red'
      },
      timeAgo(dateStr) {
        if (!dateStr) return ''
        const now = new Date()
        const past = new Date(dateStr)
        const diffMs = now - past
        const diffSeconds = Math.floor(diffMs / 1000)
        if (diffSeconds < 0) return 'right now'
        if (diffSeconds < 60) return diffSeconds + ' seconds ago'
        const diffMinutes = Math.floor(diffSeconds / 60)
        if (diffMinutes < 60) return diffMinutes + ' minutes ago'
        const diffHours = Math.floor(diffMinutes / 60)
        if (diffHours < 24) return diffHours + ' hours ago'
        const diffDays = Math.floor(diffHours / 24)
        if (diffDays < 7) return diffDays + ' days ago'
        if (diffDays < 30) return diffDays + ' days ago'
        const diffMonths = Math.floor(diffDays / 30)
        if (diffMonths < 12) return diffMonths + ' months ago'
        const diffYears = Math.floor(diffMonths / 12)
        return diffYears + ' years ago'
      },
      customSort(items, sortBy, sortDesc) {
        if (!sortBy.length) {
          return items.sort((a, b) => {
            if (a._empty && !b._empty) return 1
            if (!a._empty && b._empty) return -1
            return (a.id || 0) - (b.id || 0)
          })
        }
        const field = sortBy[0]
        return items.sort((a, b) => {
          if (a._empty && !b._empty) return 1
          if (!a._empty && b._empty) return -1
          if (a._empty && b._empty) return 0
          let comp = 0
          if (field === 'role') {
            const order = { annotator: 0, admin: 1, owner: 2 }
            comp = order[a.role] - order[b.role]
          } else if (field === 'date_joined') {
            comp = new Date(a.date_joined) - new Date(b.date_joined)
          } else if (field === 'last_seen') {
            comp = new Date(a.last_login) - new Date(b.last_login)
          } else if (field === 'id') {
            comp = (a.id || 0) - (b.id || 0)
          } else if (typeof a[field] === 'string') {
            comp = a[field].localeCompare(b[field])
          } else {
            comp = (a[field] || 0) - (b[field] || 0)
          }
          return sortDesc[0] ? -comp : comp
        })
      }
    }
  }
  </script>
  
  <style scoped>
  .v-card {
    background-color: #ffffff;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  .v-container {
    padding: 20px;
  }
  .v-data-table {
    margin-top: 20px;
  }
  .v-pagination {
    margin-top: 10px;
  }
  ::v-deep tr.dummy-row:hover {
    background-color: transparent !important;
  }
  .status-circle {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    position: relative;
    z-index: 1;
  }
  
  .theme--dark .v-card {
    background-color: #1e1e1e !important;
    color: #ffffff;
  }
  
  .theme--dark .v-text-field input {
    color: #ffffff;
  }
  
  .theme--dark .v-select .v-input__slot {
    background-color: #0f0f0f !important;
    color: #ffffff;
  }
  
  .theme--dark .v-text-field {
    background-color: #1e1e1e !important;
    color: #ffffff;
  }
  
  .theme--dark .v-text-field :hover {
    background-color: #191919 !important;
    color: #ffffff;
  }
  
  .theme--dark .v-text-field input {
    color: #ffffff;
  }
  
  :deep(.theme--dark .v-data-table tbody tr:hover:not(.dummy-row)) {
    background-color: #151515 !important;
  }
  </style>