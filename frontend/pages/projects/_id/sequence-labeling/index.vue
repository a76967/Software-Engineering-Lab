<template>
  <div>
    <!-- 1) alerta sempre visível se houver erro de BD -->
    <v-alert
      v-if="dbError"
      type="error"
      dense
      class="mb-4"
    >
      {{ dbError }}
    </v-alert>

    <!-- 2) resto só se houver doc -->
    <layout-text v-if="doc.id" v-shortkey="shortKeys" @shortkey="changeSelectedLabel">
      <template #header>
        <toolbar-laptop
          :doc-id="doc.id"
          :enable-auto-labeling.sync="enableAutoLabeling"
          :guideline-text="project.guideline"
          :is-reviewd="doc.isConfirmed"
          :total="docs.count"
          class="d-none d-sm-block"
          @click:clear-label="clear"
          @click:review="confirm"
        />
        <toolbar-mobile :total="docs.count" class="d-flex d-sm-none" />
      </template>
      <template #content>
        <v-card>
          <div class="annotation-text pa-4">
            <entity-editor
              :dark="$vuetify.theme.dark"
              :rtl="isRTL"
              :text="doc.text"
              :entities="annotations"
              :entity-labels="spanTypes"
              :relations="relations"
              :relation-labels="relationTypes"
              :allow-overlapping="project.allowOverlappingSpans"
              :grapheme-mode="project.enableGraphemeMode"
              :selected-label="selectedLabel"
              :relation-mode="relationMode"
              @addEntity="addSpan"
              @addRelation="addRelation"
              @click:entity="updateSpan"
              @click:relation="updateRelation"
              @contextmenu:entity="deleteSpan"
              @contextmenu:relation="deleteRelation"
            />
          </div>
        </v-card>
      </template>
      <template #sidebar>
        <annotation-progress :progress="progress" />
        <v-card class="mt-4">
          <v-card-title>
            Label Types
            <v-spacer />
            <v-btn icon @click="showLabelTypes = !showLabelTypes">
              <v-icon>{{ showLabelTypes ? mdiChevronUp : mdiChevronDown }}</v-icon>
            </v-btn>
          </v-card-title>
          <v-expand-transition>
            <v-card-text v-show="showLabelTypes">
              <v-switch v-if="useRelationLabeling" v-model="relationMode">
                <template #label>
                  <span v-if="relationMode">Relation</span>
                  <span v-else>Span</span>
                </template>
              </v-switch>
              <v-chip-group v-model="selectedLabelIndex" column>
                <v-chip
                  v-for="(item, index) in labelTypes"
                  :key="item.id"
                  v-shortkey="[item.suffixKey]"
                  :color="item.backgroundColor"
                  filter
                  :text-color="$contrastColor(item.backgroundColor)"
                  @shortkey="selectedLabelIndex = index"
                >
                  {{ item.text }}
                  <v-avatar
                    v-if="item.suffixKey"
                    right
                    color="white"
                    class="black--text font-weight-bold"
                  >
                    {{ item.suffixKey }}
                  </v-avatar>
                </v-chip>
              </v-chip-group>
            </v-card-text>
          </v-expand-transition>
        </v-card>
        <list-metadata :metadata="doc.meta" class="mt-4" />
      </template>
    </layout-text>
  </div>
</template>

<script>
import { mdiChevronDown, mdiChevronUp } from '@mdi/js'
import _ from 'lodash'
import { mapGetters } from 'vuex'
import LayoutText from '@/components/tasks/layout/LayoutText'
import ListMetadata from '@/components/tasks/metadata/ListMetadata'
import EntityEditor from '@/components/tasks/sequenceLabeling/EntityEditor.vue'
import AnnotationProgress from '@/components/tasks/sidebar/AnnotationProgress.vue'
import ToolbarLaptop from '@/components/tasks/toolbar/ToolbarLaptop'
import ToolbarMobile from '@/components/tasks/toolbar/ToolbarMobile'

export default {
  components: {
    AnnotationProgress,
    EntityEditor,
    LayoutText,
    ListMetadata,
    ToolbarLaptop,
    ToolbarMobile
  },

  layout: 'workspace',

  validate({ params, query }) {
    return /^\d+$/.test(params.id) && /^\d+$/.test(query.page)
  },

  data() {
    return {
      annotations: [],
      docs: [],
      spanTypes: [],
      relations: [],
      relationTypes: [],
      project: {},
      enableAutoLabeling: false,
      rtl: false,
      selectedLabelIndex: null,
      progress: {},
      relationMode: false,
      showLabelTypes: true,
      mdiChevronUp,
      mdiChevronDown,
      dbError: ''
    }
  },

  async fetch() {
    try {
      this.dbError = ''
      this.docs = await this.$services.example.fetchOne(
        this.projectId,
        this.$route.query.page,
        this.$route.query.q,
        this.$route.query.isChecked,
        this.$route.query.ordering
      )
      const doc = this.docs.items[0]
      if (this.enableAutoLabeling && !doc.isConfirmed) {
        await this.autoLabel(doc.id)
      }
      await this.list(doc.id)
    } catch (err) {
      console.error('Error fetching sequence-labeling data:', err.response || err.message || err)
      this.dbError = "Error: Can't access our database!"
    }
  },

  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'getUsername', 'getUserId']),
    ...mapGetters('config', ['isRTL']),

    shortKeys() {
      return Object.fromEntries(this.spanTypes.map((item) => [item.id, [item.suffixKey]]))
    },

    projectId() {
      return this.$route.params.id
    },

    doc() {
      if (_.isEmpty(this.docs) || this.docs.items.length === 0) {
        return {}
      } else {
        return this.docs.items[0]
      }
    },

    selectedLabel() {
      if (Number.isInteger(this.selectedLabelIndex)) {
        if (this.relationMode) {
          return this.relationTypes[this.selectedLabelIndex]
        } else {
          return this.spanTypes[this.selectedLabelIndex]
        }
      } else {
        return null
      }
    },

    useRelationLabeling() {
      return !!this.project.useRelation
    },

    labelTypes() {
      if (this.relationMode) {
        return this.relationTypes
      } else {
        return this.spanTypes
      }
    }
  },

  watch: {
    '$route.query': '$fetch',
    async enableAutoLabeling(val) {
      if (val && !this.doc.isConfirmed) {
        await this.autoLabel(this.doc.id)
        await this.list(this.doc.id)
      }
    }
  },

  async created() {
    this.spanTypes = await this.$services.spanType.list(this.projectId)
    this.relationTypes = await this.$services.relationType.list(this.projectId)
    this.project = await this.$services.project.findById(this.projectId)
    this.progress = await this.$repositories.metrics.fetchMyProgress(this.projectId)
  },

  methods: {
    async maybeFetchSpanTypes(annotations) {
      const labelIds = new Set(this.spanTypes.map((label) => label.id))
      if (annotations.some((item) => !labelIds.has(item.label))) {
        this.spanTypes = await this.$services.spanType.list(this.projectId)
      }
    },

    async list(docId) {
      const annotations = await this.$services.sequenceLabeling.list(this.projectId, docId)
      const relations = await this.$services.sequenceLabeling.listRelations(this.projectId, docId)
      await this.maybeFetchSpanTypes(annotations)
      this.annotations = annotations
      this.relations = relations
    },

    async deleteSpan(id) {
      await this.$services.sequenceLabeling.delete(this.projectId, this.doc.id, id)
      await this.list(this.doc.id)
    },

    async addSpan(startOffset, endOffset, labelId) {
      await this.$services.sequenceLabeling.create(
        this.projectId,
        this.doc.id,
        labelId,
        startOffset,
        endOffset
      )
      await this.list(this.doc.id)
    },

    async updateSpan(annotationId, labelId) {
      await this.$services.sequenceLabeling.changeLabel(
        this.projectId,
        this.doc.id,
        annotationId,
        labelId
      )
      await this.list(this.doc.id)
    },

    async addRelation(fromId, toId, typeId) {
      await this.$services.sequenceLabeling.createRelation(
        this.projectId,
        this.doc.id,
        fromId,
        toId,
        typeId
      )
      await this.list(this.doc.id)
    },

    async updateRelation(relationId, typeId) {
      await this.$services.sequenceLabeling.updateRelation(
        this.projectId,
        this.doc.id,
        relationId,
        typeId
      )
      await this.list(this.doc.id)
    },

    async deleteRelation(relationId) {
      await this.$services.sequenceLabeling.deleteRelation(this.projectId, this.doc.id, relationId)
      await this.list(this.doc.id)
    },

    async clear() {
      await this.$services.sequenceLabeling.clear(this.projectId, this.doc.id)
      await this.list(this.doc.id)
    },

    async autoLabel(docId) {
      try {
        await this.$services.sequenceLabeling.autoLabel(this.projectId, docId)
      } catch (e) {
        console.log(e.response.data.detail)
      }
    },

    async updateProgress() {
      this.progress = await this.$repositories.metrics.fetchMyProgress(this.projectId)
    },

    async confirm() {
      await this.$services.example.confirm(this.projectId, this.doc.id)
      await this.$fetch()
      this.updateProgress()
    },

    changeSelectedLabel(event) {
      this.selectedLabelIndex = this.spanTypes.findIndex((item) => item.suffixKey === event.srcKey)
    }
  }
}
</script>

<style scoped>
.annotation-text {
  font-size: 1.25rem !important;
  font-weight: 500;
  line-height: 2rem;
  font-family: 'Roboto', sans-serif !important;
  opacity: 0.6;
}
</style>
