<template>
  <v-list dense>
    <v-btn color="ms-4 my-1 mb-2 primary text-capitalize" nuxt @click="toLabeling">
      <v-icon left>
        {{ mdiPlayCircleOutline }}
      </v-icon>
      {{ $t('home.startAnnotation') }}
    </v-btn>
    <v-list-item-group v-model="selected" mandatory>
      <v-list-item
        v-for="(item, i) in filteredItems"
        :key="i"
        @click="$router.push(localePath(`/projects/${$route.params.id}/${item.link}`))"
      >
        <v-list-item-action>
          <v-icon>
            {{ item.icon }}
          </v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title>
            {{ item.text }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list-item-group>
  </v-list>
</template>

<script>
import {
  mdiAccount,
  mdiAccountGroup,
  mdiBookOpenOutline,
  mdiChartBar,
  mdiCog,
  mdiCommentAccountOutline,
  mdiDatabase,
  mdiAccountEye,
  mdiEye,
  mdiGavel,
  mdiHome,
  mdiLabel,
  mdiPlayCircleOutline,
  mdiThumbDownOutline,
  mdiVote,
  mdiFileChartOutline,
} from '@mdi/js'
import { getLinkToAnnotationPage } from '~/presenter/linkToAnnotationPage'

export default {
  props: {
    isProjectAdmin: {
      type: Boolean,
      default: false,
      required: true
    },
    project: {
      type: Object,
      default: () => {},
      required: true
    }
  },

  data() {
    return {
      selected: 0,
      mdiPlayCircleOutline,
      mdiThumbDownOutline,
      mdiVote
    }
  },

  computed: {
    filteredItems() {
      const items = [
        {
          icon: mdiHome,
          text: this.$t('projectHome.home'),
          link: '',
          isVisible: true
        },
        {
          icon: mdiDatabase,
          text: this.$t('dataset.dataset'),
          link: 'dataset',
          isVisible: true
        },
        {
          icon: mdiLabel,
          text: this.$t('labels.labels'),
          link: 'labels',
          isVisible:
            (this.isProjectAdmin || this.project.allowMemberToCreateLabelType) &&
            this.project.canDefineLabel
        },
        {
          icon: mdiLabel,
          text: 'Relations',
          link: 'links',
          isVisible:
            false
        },
        {
          icon: mdiAccount,
          text: this.$t('members.members'),
          link: 'members',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiCommentAccountOutline,
          text: 'Comments',
          link: 'comments',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiEye,
          text: 'Admin Perspectives',
          link: 'admin-perspectives',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiAccountEye,
          text: 'User Perspectives',
          link: 'perspectives',
          isVisible: true
        },
        {
          icon: this.mdiThumbDownOutline,
          text: 'Disagreements',
          link: 'disagreements',
          isVisible: true
        },
        {
          icon: mdiAccountGroup,
          text: 'Discussions',
          link: 'discussions',
          isVisible: true
        },
        {
          icon: mdiGavel,
          text: 'Annotation Rules',
          link: 'annotation-rules',
          isVisible: false
        },
        {
          icon: mdiVote,
          text: 'Voting',
          link: 'voting',
          isVisible: true
        },
        {
          icon: mdiFileChartOutline,
          text: 'Reports',
          link: 'reports',
          isVisible: true
        },
        {
          icon: mdiBookOpenOutline,
          text: this.$t('guideline.guideline'),
          link: 'guideline',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiChartBar,
          text: this.$t('statistics.statistics'),
          link: 'metrics',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiCog,
          text: this.$t('settings.title'),
          link: 'settings',
          isVisible: this.isProjectAdmin
        },
      ]
      return items.filter((item) => item.isVisible)
    }
  },

  methods: {
    toLabeling() {
      const query = this.$services.option.findOption(this.$route.params.id)
      const link = getLinkToAnnotationPage(this.$route.params.id, this.project.projectType)
      this.$router.push({
        path: this.localePath(link),
        query
      })
    }
  }
}
</script>
