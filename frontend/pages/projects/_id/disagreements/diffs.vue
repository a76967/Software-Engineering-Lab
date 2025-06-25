<template>
  <div class="diffs-container">
    <div id="diffs-wrapper" style="position: relative;">
      <v-card>
        <v-card-title class="black--text text-center">
          <span class="headline">Differences</span>
          <v-chip-group column>
            <v-chip
              v-for="(label, idx) in allLabels"
              :key="idx"
              :color="label.color"
              :text-color="contrastColor(label.color)"
              small
              class="ma-1 non-clickable"
            >
              {{ label.text }}
            </v-chip>
          </v-chip-group>
        </v-card-title>
        <v-card-text>
          <v-progress-circular
            v-if="isLoading"
            indeterminate
            color="primary"
            class="ma-3"
          />
          <v-alert v-if="error" type="error" dense class="mb-4">
            {{ error }}
          </v-alert>
          <div v-if="!isLoading && annotations.length < 2">
            <p>Not enough annotations to compare.</p>
          </div>
          <div v-if="!isLoading && annotations.length >= 2" class="diff-container">

            <v-card class="diff-card" outlined>
              <v-card-title class="primary white--text text-center">
                Left
              </v-card-title>
              <v-card-text class="diff-canvas">
                <div
                  v-if="leftAnnotation"
                  class="diff-annotation-text"
                  v-html="formattedLeftText"
                ></div>
              </v-card-text>
              <v-card-actions class="justify-center">
                <v-btn
                  small
                  :disabled="
                    navigationDisabled ||
                    leftIndex === 0
                  "
                  @click="prevLeft"
                >
                  Prev
                </v-btn>
                <v-btn
                  small
                  :disabled="
                    navigationDisabled ||
                    leftIndex === annotations.length - 1
                  "
                  @click="nextLeft"
                >
                  Next
                </v-btn>
              </v-card-actions>
            </v-card>

            <div class="switch-button">
              <v-btn icon @click="swapAnnotations">
                <v-icon>{{ icons.mdiSwapHorizontal }}</v-icon>
              </v-btn>
            </div>

            <v-card class="diff-card" outlined>
              <v-card-title class="primary white--text text-center">
                Right
              </v-card-title>
              <v-card-text class="diff-canvas">
                <div
                  v-if="rightAnnotation"
                  class="diff-annotation-text"
                  v-html="formattedRightText"
                ></div>
              </v-card-text>
              <v-card-actions class="justify-center">
                <v-btn
                  small
                  :disabled="
                    navigationDisabled ||
                    rightIndex === 0
                  "
                  @click="prevRight"
                >
                  Prev
                </v-btn>
                <v-btn
                  small
                  :disabled="
                    navigationDisabled ||
                    rightIndex === annotations.length - 1
                  "
                  @click="nextRight"
                >
                  Next
                </v-btn>
              </v-card-actions>
            </v-card>
          </div>
          <v-checkbox v-model="showDifferences" 
          label="Toggle Differences" class="mt-2"></v-checkbox>
        </v-card-text>

        <v-card-text>
          <div class="text-center mb-4">
            <div>
              Left side: 
              <strong>{{ leftCount }}</strong>
              <span v-if="userVotedSide==='left'"> (You) </span>
            </div>
            <div>
              Right side: 
              <strong>{{ rightCount }}</strong>
              <span v-if="userVotedSide==='right'"> (You) </span>
            </div>
          </div>

          <div class="text-center mb-2">
            <strong>Winner: </strong>
            <span v-if="winner==='left'">Left side</span>
            <span v-else-if="winner==='right'">Right side</span>
            <span v-else>Tie</span>
          </div>

          <!-- escolha -->
          <v-radio-group 
            v-model="selectedSide" 
            row 
            :disabled="!!userVotedSide"
          >
            <v-radio label="Left side"  value="left"  />
            <v-radio label="Right side" value="right" />
          </v-radio-group>
        </v-card-text>

        <v-card-actions>
          <v-spacer/>
          <v-btn 
            color="primary" 
            @click="confirmResolve"
            :disabled="!selectedSide || !!userVotedSide"
          >
            Solve
          </v-btn>
        </v-card-actions>

        <v-dialog v-model="showResolveDialog" max-width="400px">
          <v-card>
            <v-card-title class="headline">Solve Disagreement</v-card-title>
            <v-card-text>
              <v-radio-group
                v-model="selectedSide"
                row
                class="justify-space-between"
              >
                <v-radio label="Left side" value="left" />
                <v-radio label="Right side" value="right" />
              </v-radio-group>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn text @click="showResolveDialog = false">Cancel</v-btn>
              <v-btn color="primary" @click="confirmResolve">Confirm</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-card>

      <v-btn
        fixed
        right
        color="primary"
        dark
        fab
        small
        @click="drawer = true"
        style="top: 50vh; transform: translateY(-50%);"
      >
        <v-icon>mdi-comment-plus</v-icon>
      </v-btn>

      <v-navigation-drawer
        v-model="drawer"
        attach="#diffs-wrapper"
        absolute
        right
        temporary
        width="300"
        elevation="2"
      >
        <v-toolbar flat dense>
          <v-toolbar-title>Comentários</v-toolbar-title>
          <v-spacer/>
          <v-btn icon @click="drawer = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
        <v-divider/>

        <v-list dense two-line subheader>
          <v-subheader>Últimos comentários</v-subheader>
          <v-list-item
            v-for="c in comments"
            :key="c.id"
          >
            <v-list-item-content>
              <v-list-item-title>{{ c.text }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ new Date(c.created_at).toLocaleString() }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>

        <v-divider class="my-2"/>
        <v-card-text>
          <v-textarea
            v-model="commentText"
            label="Escreva um comentário"
            auto-grow
            rows="3"
          />
          <v-btn
            class="mt-4"
            block
            color="primary"
            :disabled="!commentText.trim()"
            @click="sendComment"
          >
            Enviar
          </v-btn>
        </v-card-text>
      </v-navigation-drawer>
    </div>
  </div>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'
import { mdiSwapHorizontal } from '@mdi/js'
import { mapState } from 'vuex'

export default Vue.extend({
  name: 'DiffsPage',

  layout: 'project',

  data() {
    return {
      annotations: [] as AnnotationTransformed[],
      leftIndex: 0,
      rightIndex: 1,
      isLoading: false,
      error: '',
      icons: { mdiSwapHorizontal },
      isRTL: false,
      showDifferences: false,
      showResolveDialog: false,
      selectedSide: '' as 'left'|'right'|'',
      userVotedSide: '' as 'left'|'right'|'',
      leftCount: 0,
      rightCount: 0,
      drawer: false,
      commentText: '',
      comments: [] as Array<{ id: number, text: string, created_at: string }>
    }
  },

  computed: {
    ...mapState('auth', {
      currentUsername: (s: any) => s.username
    }),
    navigationDisabled(): boolean {
      return this.annotations.length === 2;
    },
    leftAnnotation(): AnnotationTransformed | null {
      return this.annotations[this.leftIndex] || null;
    },
    rightAnnotation(): AnnotationTransformed | null {
      return this.annotations[this.rightIndex] || null;
    },
    formattedLeftText(): string {
      return (this.leftAnnotation && this.rightAnnotation) ? this.generateAnnotatedText(this.leftAnnotation, this.rightAnnotation) : "";
    },
    formattedRightText(): string {
      return (this.rightAnnotation && this.leftAnnotation) ? this.generateAnnotatedText(this.rightAnnotation, this.leftAnnotation) : "";
    },
    allLabels(): Array<{ id: number; text: string; color: string }> {
      if (this.leftAnnotation && this.leftAnnotation.entityLabels) {
        const seen = new Set();
        return this.leftAnnotation.entityLabels.filter(label => {
          if (seen.has(label.id)) return false;
          seen.add(label.id);
          return true;
        }).map(label => ({
          id: label.id,
          text: label.text,
          color: label.color
        }));
      }
      return [];
    },
    winner(): 'left'|'right'|'tie' {
      if (this.leftCount > this.rightCount)  return 'left'
      if (this.rightCount > this.leftCount) return 'right'
      return 'tie'
    }
  },
  async mounted() {
    await this.fetchAnnotations()
    this.initVoteState()
    await this.fetchComments()
  },
  methods: {
    async fetchAnnotations() {
      this.isLoading = true;
      try {
        const response = await axios.get(`/v1/annotations/`, { params: { project: this.$route.params.id } });
        const data: AnnotationBackend[] = response.data.results || response.data;
        const groups: { [signature: string]: AnnotationBackend[] } = {};

        data.forEach(annotation => {
          const extracted = annotation.extracted_labels;
          if (!extracted || !extracted.text || !extracted.labelTypes || !extracted.spans) return;

          const usedLabelIds = new Set(extracted.spans.map((span: any) => span.label));
          const chosenLabels = extracted.labelTypes.filter(label => usedLabelIds.has(label.id));
          const sortedLabels = [...chosenLabels].sort((a, b) => a.id - b.id);

          const signatureKey = JSON.stringify({
            text: extracted.text,
            labelTypes: sortedLabels.map(label => ({ id: label.id, text: label.text }))
          });
          
          if (!groups[signatureKey]) { groups[signatureKey] = []; }
          groups[signatureKey].push(annotation);
        });

        const leftQuery = this.$route.query.left;
        const rightQuery = this.$route.query.right;
        const selectedGroup = Object.values(groups).find(group =>
          group.some(ann => String(ann.id) === leftQuery) &&
          group.some(ann => String(ann.id) === rightQuery)
        );

        if (selectedGroup && selectedGroup.length >= 2) {
          this.annotations = selectedGroup.map(ann => {
            const extracted = ann.extracted_labels;
            const usedLabelIds = new Set(extracted.spans.map((span: any) => span.label));
            const chosenLabels = extracted.labelTypes.filter(label => usedLabelIds.has(label.id));
            const sortedLabels = [...chosenLabels].sort((a, b) => a.id - b.id);
            const labels = sortedLabels.map(label => ({
              id: label.id,
              text: label.text,
              color: label.background_color,
              textColor: label.text_color || '#ffffff',
              suffixKey: label.suffixKey ? label.suffixKey : label.text
            }));
            return {
              id: ann.id,
              text: extracted.text,
              entities: extracted.spans.map((span, i) => ({
                id: i,
                start: span.start_offset,
                end: span.end_offset,
                label: labels.find(l => l.id === span.label) || { id: span.label, text: '', color: '#000000', textColor: '#ffffff', suffixKey: '' }
              })),
              entityLabels: labels
            };
          });
          this.leftIndex = 0;
          this.rightIndex = 1;
        } else {
          this.error = 'No matching disagreement group found.';
          this.annotations = [];
        }
      } catch (err: any) {
        console.error(err);
        this.error = "Error: Can't access our database!";
      } finally {
        this.isLoading = false;
      }
    },
    async fetchComments() {
      const projectId = this.$route.params.id as string
      const exampleId = this.$route.query.left as string
      try {
        const res = await axios.get(
          `/v1/projects/${projectId}/comments/`,
          { params: { example: exampleId } }
        )
        this.comments = res.data.results || res.data
      } catch (err) {
        console.warn('Não foi possível carregar comentários', err)
        this.comments = []
      }
    },
    generateAnnotatedText(annotation: AnnotationTransformed, other: AnnotationTransformed): string {
      const escapeHTML = (str: string) =>
        str.replace(/&/g, "&amp;")
           .replace(/</g, "&lt;")
           .replace(/>/g, "&gt;");
      const text = annotation.text;

      const boundaries = new Set<number>();
      annotation.entities.forEach(span => {
        boundaries.add(span.start);
        boundaries.add(span.end);
      });
      other.entities.forEach(span => {
        boundaries.add(span.start);
        boundaries.add(span.end);
      });

      const sortedBoundaries = Array.from(boundaries).sort((a, b) => a - b);
      let html = "";

      for (let i = 0; i < sortedBoundaries.length - 1; i++) {
        const start = sortedBoundaries[i];
        const end = sortedBoundaries[i + 1];
        const segment = text.substring(start, end);

        const currentSpan = annotation.entities.find(s => s.start <= start && s.end >= end);
        const otherSpan = other.entities.find(s => s.start <= start && s.end >= end);

        let style = "";
        if (currentSpan) {
          style = `border-bottom: 3px solid ${currentSpan.label.color};`;
        }
        if (this.showDifferences && otherSpan) {
          if (!currentSpan || (currentSpan && currentSpan.label.id !== otherSpan.label.id)) {
            style = 'border-bottom: 3px dashed #FF5252;';
          }
        }

        html += `<span style="${style}" title="${currentSpan ? currentSpan.label.text : (otherSpan ? otherSpan.label.text : '')}">${escapeHTML(segment)}</span>`;
      }

      const firstBoundary = sortedBoundaries[0] || 0;
      const prefix = text.substring(0, firstBoundary);
      const lastBoundary = sortedBoundaries[sortedBoundaries.length - 1] || text.length;
      const suffix = text.substring(lastBoundary);

      html = (prefix ? escapeHTML(prefix) : "") + html + (suffix ? escapeHTML(suffix) : "");
      return html;
    },
    swapAnnotations() {
      const temp = this.leftIndex;
      this.leftIndex = this.rightIndex;
      this.rightIndex = temp;
    },
    prevLeft() {
      if (this.leftIndex > 0) {
        this.leftIndex--;
        if (this.leftIndex === this.rightIndex) {
          this.leftIndex > 0 ? this.leftIndex-- : this.leftIndex++;
        }
      }
    },
    nextLeft() {
      if (this.leftIndex < this.annotations.length - 1) {
        this.leftIndex++;
        if (this.leftIndex === this.rightIndex) {
          this.leftIndex < this.annotations.length - 1 ? this.leftIndex++ : this.leftIndex--;
        }
      }
    },
    prevRight() {
      if (this.rightIndex > 0) {
        this.rightIndex--;
        if (this.rightIndex === this.leftIndex) {
          this.rightIndex > 0 ? this.rightIndex-- : this.rightIndex++;
        }
      }
    },
    nextRight() {
      if (this.rightIndex < this.annotations.length - 1) {
        this.rightIndex++;
        if (this.rightIndex === this.leftIndex) {
          this.rightIndex < this.annotations.length - 1 ? this.rightIndex++ : this.rightIndex--;
        }
      }
    },
    checkDisagreement() {
      const projectId = this.$route.params.id;
      const leftId = this.leftAnnotation ? String(this.leftAnnotation.id) : '';
      const rightId = this.rightAnnotation ? String(this.rightAnnotation.id) : '';
      this.$router.push({
        path: `/projects/${projectId}/disagreements/diffs`,
        query: { left: leftId, right: rightId }
      });
    },
    contrastColor(color: string): string {
      const r = parseInt(color.slice(1, 3), 16);
      const g = parseInt(color.slice(3, 5), 16);
      const b = parseInt(color.slice(5, 7), 16);
      const brightness = (r * 299 + g * 587 + b * 114) / 1000;
      return brightness > 125 ? 'black' : 'white';
    },
    openResolveDialog() {
      this.showResolveDialog = true;
    },
    initVoteState() {
      const projectId = this.$route.params.id as string
      const leftId    = String(this.leftAnnotation?.id||'')
      const rightId   = String(this.rightAnnotation?.id||'')
      const votesKey  = `votes_${projectId}_${leftId}_${rightId}`

      const votesRec = JSON.parse(
        localStorage.getItem(votesKey) || '{}'
      ) as Record<string,'left'|'right'>

      this.leftCount  = Object.values(votesRec).filter(v => v==='left').length
      this.rightCount = Object.values(votesRec).filter(v => v==='right').length

      this.userVotedSide = votesRec[this.currentUsername] || ''
    },
    confirmResolve() {
      if (this.userVotedSide) return

      const projectId = this.$route.params.id as string
      const leftId    = String(this.leftAnnotation!.id)
      const rightId   = String(this.rightAnnotation!.id)
      const votesKey  = `votes_${projectId}_${leftId}_${rightId}`

      const votesRec = JSON.parse(
        localStorage.getItem(votesKey) || '{}'
      ) as Record<string,'left'|'right'>
      votesRec[this.currentUsername] = this.selectedSide as 'left'|'right'
      localStorage.setItem(votesKey, JSON.stringify(votesRec))

      this.initVoteState()
    },
    async sendComment() {
      const projectId = this.$route.params.id as string
      const exampleId = this.$route.query.left as string
      try {
        await axios.post(
          `/v1/projects/${projectId}/comments/`,
          { example: exampleId, text: this.commentText }
        )
        this.commentText = ''
        await this.fetchComments()
      } catch (err) {
        console.error('Erro ao enviar comentário', err)
      }
    }
  }
});
</script>

<style scoped>
.diff-container {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  overflow-x: auto;
  gap: 16px;
  padding: 8px;
}
.diff-card {
  flex: 0 0 auto;
  width: 45%;
}
.switch-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 5%;
}
.diff-canvas {
  height: 250px;
  overflow-y: auto;
  padding: 8px;
}
.diff-annotation-text {
  font-size: 1rem !important;
  font-weight: 500;
  line-height: 1.5rem;
}
.label-legend {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 8px;
}
.legend-item {
  display: inline-flex;
  align-items: center;
  margin: 0 8px;
}
.legend-ball {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 4px;
}
.legend-text {
  font-size: 0.8rem;
}
.non-clickable {
  pointer-events: none;
}
</style>