<template>
  <v-app-bar app clipped-left>
    <slot name="leftDrawerIcon" />
    <nuxt-link to="/home" style="line-height: 0">
      <img src="/doccana-logo.png" height="48" draggable="false" />
    </nuxt-link>
    <v-btn
      v-if="isAuthenticated && isIndividualProject"
      text
      class="d-none d-sm-flex"
      style="text-transform: none"
    >
      <v-icon small class="mr-1">{{ mdiHexagonMultiple }}</v-icon>
      <span>{{ currentProject.name }}</span>
    </v-btn>
    <v-select
      v-if="isAuthenticated && isIndividualProject"
      :items="versionItems"
      item-text="text"
      item-value="id"
      hide-details
      dense
      style="max-width: 120px; margin-left: 8px"
      v-model="selectedVersion"
      @change="onChangeVersion"
    />
    <v-btn
      v-if="isAuthenticated && isIndividualProject && isProjectAdmin"
      small
      class="ms-2"
      @click="addVersion"
    >
      Add Version
    </v-btn>
    <div class="flex-grow-1" />
    <the-color-mode-switcher />

    <v-btn icon @click="dialogNotifications = true">
      <v-icon>{{ mdiBell }}</v-icon>
    </v-btn>

    <v-dialog v-model="dialogNotifications" max-width="300">
      <v-card>
        <v-card-title>No notifications</v-card-title>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialogNotifications = false">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-btn
      v-if="isAuthenticated"
      text
      class="text-capitalize"
      @click="$router.push(localePath('/projects'))"
    >
      {{ $t('header.projects') }}
    </v-btn>
    <v-menu v-if="!isAuthenticated" open-on-hover offset-y>
      <template #activator="{ on }">
        <v-btn text v-on="on">
          {{ $t('home.demoDropDown') }}
          <v-icon>{{ mdiMenuDown }}</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item
          v-for="(item, index) in items"
          :key="index"
          @click="$router.push('/demo/' + item.link)"
        >
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    <v-btn v-if="!isAuthenticated" outlined @click="$router.push(localePath('/auth'))">
      {{ $t('user.login') }}
    </v-btn>
    <v-btn
      v-if="!isAuthenticated"
      outlined
      style="margin-left: 0.5vw"
      @click="$router.push(localePath('/register'))"
    >
      Register
    </v-btn>
    <v-btn
      v-if="isAuthenticated"
      outlined
      style="margin-left: 0.5vw"
      @click="$router.push(localePath('/list-user'))"
    >
      All Users
    </v-btn>
    <v-menu v-if="isAuthenticated" offset-y z-index="200">
      <template #activator="{ on }">
        <v-btn on icon v-on="on">
          <v-icon>{{ mdiDotsVertical }}</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-subheader>{{ getUsername }}</v-subheader>
        <v-list-item>
          <v-list-item-content>
            <v-switch :input-value="isRTL" :label="direction" class="ms-1" @change="toggleRTL" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item @click="signout">
          <v-list-item-icon>
            <v-icon>{{ mdiLogout }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>
              {{ $t('user.signOut') }}
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script>
import { mdiLogout, mdiDotsVertical, mdiMenuDown, mdiHexagonMultiple, mdiBell } from '@mdi/js'
import { mapGetters, mapActions } from 'vuex'
import TheColorModeSwitcher from './TheColorModeSwitcher'

export default {
  components: {
    TheColorModeSwitcher
  },

  data() {
    return {
      items: [
        { title: this.$t('home.demoNER'), link: 'named-entity-recognition' },
        { title: this.$t('home.demoSent'), link: 'sentiment-analysis' },
        { title: this.$t('home.demoTranslation'), link: 'translation' },
        {
          title: this.$t('home.demoIntenDetectSlotFil'),
          link: 'intent-detection-and-slot-filling'
        },
        { title: this.$t('home.demoTextToSQL'), link: 'text-to-sql' },
        { title: this.$t('home.demoImageClas'), link: 'image-classification' },
        { title: this.$t('home.demoImageCapt'), link: 'image-caption' },
        { title: this.$t('home.demoObjDetect'), link: 'object-detection' },
        { title: this.$t('home.demoPolygSegm'), link: 'segmentation' },
        { title: this.$t('home.demoSTT'), link: 'speech-to-text' }
      ],
      dialogNotifications: false,
      mdiLogout,
      mdiDotsVertical,
      mdiMenuDown,
      mdiHexagonMultiple,
      mdiBell,
      selectedVersion: null
    }
  },

  computed: {
      ...mapGetters('auth', ['isAuthenticated', 'getUsername']),
      ...mapGetters('projects', ['currentProject', 'projectVersions', 'isProjectAdmin']),
      ...mapGetters('config', ['isRTL']),

      versionItems() {
        return this.projectVersions.map(v => ({ id: v.id, text: `Version ${v.versionNumber}` }))
      },

    isIndividualProject() {
      return this.$route.name && this.$route.name.startsWith('projects-id')
    },

    direction() {
      return this.isRTL ? 'RTL' : 'LTR'
    }
  },

  watch: {
    currentProject: {
      handler(p) {
        this.selectedVersion = p.id
      },
      immediate: true
    }
  },

  methods: {
    ...mapActions('auth', ['logout']),
    ...mapActions('config', ['toggleRTL']),
    ...mapActions('projects', ['createVersion', 'setCurrentProject']),
    onChangeVersion(id) {
      const version = this.projectVersions.find(v => v.id === id)
      const number = version ? version.versionNumber : ''
      this.setCurrentProject(id)
      this.$router.push({
        path: '/message',
        query: {
          message: `Changing to Version ${number} of the project`,
          redirect: `/projects/${id}`
        }
      })
    },
    async addVersion() {
      const newProject = await this.createVersion()
      const number = newProject.versionNumber
      this.setCurrentProject(newProject.id)
      this.$router.push({
        path: '/message',
        query: {
          message: `Changing to Version ${number} of the project`,
          redirect: `/projects/${newProject.id}`
        }
      })
    },
    signout() {
      this.$router.push({
        path: '/message',
        query: {
          message: `Bye ${this.getUsername}, come back soon! 🥹`,
          redirect: '/home'
        }
      })
      setTimeout(() => {
        this.$store.dispatch('auth/logout')
      }, 500)
    }
  }
}
</script>
