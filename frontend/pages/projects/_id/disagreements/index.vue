<template>
  <v-card>
    <v-card-title>
      <v-btn
        class="text-capitalize ms-2"
        outlined
        @click="clearDisagreements"
      >
        Clear
      </v-btn>
    </v-card-title>
    <v-card-text>
      <v-text-field
        v-model="search"
        :prepend-inner-icon="icons.mdiMagnify"
        label="Search"
        single-line
        hide-details
        filled
        class="mb-4"
      />
      <v-progress-circular
        v-if="isLoading"
        class="ma-3"
        indeterminate
        color="primary"
      />
      <v-alert v-if="error" type="error" dense class="mb-4">
        {{ error }}
      </v-alert>
      <div v-if="!isLoading && disagreements.length === 0">
        <p>No disagreements found.</p>
      </div>
      <div v-if="!isLoading && disagreements.length > 0" class="horizontal-scroll-container">
        <div
          v-for="disagreement in filteredDisagreements"
          :key="disagreement.signature"
          class="disagreement-block"
        >
          <v-card outlined class="pa-3">
            <v-sheet color="primary" dark class="pa-2 mb-2 rounded-t-lg">
              <div class="text-h6 font-weight-medium">
                {{ disagreement.snippet }}
              </div>
            </v-sheet>

            <div class="d-flex flex-wrap mb-2">
              <v-chip
                v-for="(label, idx) in disagreement.labels"
                :key="idx"
                :color="label.backgroundColor"
                :text-color="contrastColor(label.backgroundColor)"
                small
                class="ma-1"
              >
                {{ label.text }}
              </v-chip>
            </div>

            <div class="mb-2 text-center">
              <strong>Annotations in conflict:</strong> {{ disagreement.count }}
            </div>
            <v-card-actions class="justify-center">
              <v-btn color="secondary" small @click="checkDisagreement(disagreement)">
                Check Disagreement
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'
import { mdiMagnify, mdiAlertCircle } from '@mdi/js'

interface LabelType {
  id: number;
  text: string;
  background_color: string;
}

interface ExtractedLabels {
  text: string;
  spans: any;
  labelTypes: LabelType[];
}

interface Annotation {
  id: number;
  dataset_item_id: number;
  extracted_labels: ExtractedLabels;
  additional_info: any;
  created_at: string;
  updated_at: string;
  annotator: number;
}

export default Vue.extend({
  name: 'DisagreementsPage',

  layout: 'project',

  data() {
    return {
      disagreements: [] as Array<{
        signature: string;
        snippet: string;
        labels: Array<{ text: string; backgroundColor: string }>;
        count: number;
        annotations: Annotation[];
      }>,
      search: '',
      isLoading: false,
      error: '',
      icons: {
        mdiMagnify,
        mdiAlertCircle
      }
    }
  },

  computed: {
    filteredDisagreements() {
      const disagreements = (this as any).disagreements;
      if (!this.search) return disagreements;
      return disagreements.filter((disagreement: any) =>
        disagreement.snippet.toLowerCase().includes(this.search.toLowerCase())
      );
    },
    canDelete(): boolean {
      return false;
    }
  },
  mounted() {
    this.fetchDisagreements();
  },
  methods: {
    async fetchDisagreements() {
      this.isLoading = true;
      const projectId = Number(this.$route.params.id);
      try {
        const [examplesRes, spanTypeRes] = await Promise.all([
          axios.get(`/v1/projects/${projectId}/examples`, { params: { limit: 10000 } }),
          axios.get(`/v1/projects/${projectId}/span-types`)
        ]);

        const examples = examplesRes.data.results || examplesRes.data;
        const spanTypes = spanTypeRes.data.results || spanTypeRes.data;
        const labelMap: Record<number, { text: string; background_color: string }> = {};
        spanTypes.forEach((lt: any) => {
          labelMap[lt.id] = { text: lt.text, background_color: lt.background_color };
        });

        const disagreements: any[] = [];

        for (const ex of examples) {
          const assignedUsers = (ex.assignments || []).map((a: any) => a.assignee_id);
          if (assignedUsers.length < 2) continue;

          const spansRes = await axios.get(`/v1/projects/${projectId}/examples/${ex.id}/spans`);
          const spans = spansRes.data.results || spansRes.data;

          const userSpans: Record<number, any[]> = {};
          assignedUsers.forEach((uid: number) => { userSpans[uid] = []; });
          spans.forEach((span: any) => {
            if (Object.prototype.hasOwnProperty.call(userSpans, span.user)) {
              userSpans[span.user].push(span);
            }
          });

          const signatures = assignedUsers.map(uid => {
            const list = userSpans[uid] || [];
            const simple = list
              .map((s: any) => ({
                start: s.start_offset,
                end: s.end_offset,
                label: s.label
              }))
              .sort((a, b) => {
                if (a.start !== b.start) return a.start - b.start;
                if (a.end !== b.end) return a.end - b.end;
                return a.label - b.label;
              });
            return JSON.stringify(simple);
          });

          const uniqueSignatures = new Set(signatures);
          if (uniqueSignatures.size > 1) {
            const labelIds = new Set(spans.map((s: any) => s.label));
            const labels = Array.from(labelIds).map(id => ({
              text: labelMap[id]?.text || `Label ${id}`,
              backgroundColor: labelMap[id]?.background_color || '#cccccc'
            }));

            disagreements.push({
              signature: String(ex.id),
              snippet: (ex.text || '').substring(0, 100),
              labels,
              count: assignedUsers.length,
              annotations: []
            });
          }
        }

        this.disagreements = disagreements;
      } catch (err: any) {
        console.error('Error fetching spans:', err.response || err.message);
        this.error = "Error: Can't access our database!";
      } finally {
        this.isLoading = false;
      }
    },
    clearDisagreements() {
      this.disagreements = [];
    },
    checkDisagreement(disagreement: any) {
      const projectId = this.$route.params.id;
      const leftId = disagreement.annotations[0] ? disagreement.annotations[0].id : null;
      const rightId = disagreement.annotations[1] ? disagreement.annotations[1].id : null;
      this.$router.push({
        path: `/projects/${projectId}/disagreements/diffs`,
        query: { left: leftId, right: rightId }
      });
    },
    goToAdd() {
      this.$router.push({ name: 'AddDisagreement' });
    },

    contrastColor(hexColor: string): string {
      if (!hexColor) return '#000000';
      const hex = hexColor.replace('#', '');
      let r: number, g: number, b: number;
      if (hex.length === 3) {
        r = parseInt(hex[0] + hex[0], 16);
        g = parseInt(hex[1] + hex[1], 16);
        b = parseInt(hex[2] + hex[2], 16);
      } else {
        r = parseInt(hex.substring(0, 2), 16);
        g = parseInt(hex.substring(2, 4), 16);
        b = parseInt(hex.substring(4, 6), 16);
      }
      const brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
      return brightness < 0.5 ? '#FFFFFF' : '#000000';
    }
  }
});
</script>

<style scoped>
.horizontal-scroll-container {
  display: flex;
  flex-direction: row;
  overflow-x: auto;
  padding: 8px;
}
.disagreement-block {
  flex: 0 0 auto;
  width: 300px;
  margin-right: 16px;
}
</style>