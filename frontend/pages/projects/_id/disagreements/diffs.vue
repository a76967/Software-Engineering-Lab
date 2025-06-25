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
        class="comment-btn"
        @click="drawer = true"
        style="top: 50vh; transform: translateY(-50%);"
      >
        <span class="comment-text">COMMENT</span>
      </v-btn>

      <v-navigation-drawer
        v-model="drawer"
        attach="#diffs-wrapper"
        absolute
        right
        temporary
        width="300"
        elevation="2"
        class="d-flex flex-column pa-0"
      >
        <v-toolbar flat dense>
          <v-toolbar-title>Comments</v-toolbar-title>
        </v-toolbar>
        <v-divider/>

        <v-list dense two-line subheader class="comments-list">
          <v-subheader>Last comments</v-subheader>
          <v-list-item
            v-for="c in comments"
            :key="c.id"
          >
            <v-list-item-content>
              <v-list-item-title>
                <strong>{{ c.user_name }}</strong>
                <span class="grey--text text--darken-1" style="font-size:0.75rem; margin-left:4px;">
                  {{ formatDate(c.created_at) }}
                </span>
              </v-list-item-title>
              <v-list-item-subtitle>{{ c.text }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>

        <v-divider class="my-2"/>
        <v-card-text class="form-container">
          <v-form @submit.prevent="sendComment">
            <v-textarea
              v-model="commentText"
              label="Write a comment here…"
              auto-grow
              rows="3"
              outlined
            />
            <v-row class="mt-4" dense>
              <v-col cols="6">
                <v-btn
                  block
                  color="primary"
                  type="submit"
                  :disabled="!commentText.trim()"
                >Send</v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn
                  block
                  text
                  color="primary"
                  @click="drawer = false"
                >Cancel</v-btn>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
      </v-navigation-drawer>
    </div>
  </div>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import axios from 'axios'
import { mdiSwapHorizontal, mdiChatOutline } from '@mdi/js'
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
      icons: { mdiSwapHorizontal, mdiChatOutline },
      isRTL: false,
      showDifferences: false,
      showResolveDialog: false,
      selectedSide: '' as 'left'|'right'|'',
      userVotedSide: '' as 'left'|'right'|'',
      leftCount: 0,
      rightCount: 0,
      drawer: false,
      commentText: '',
      comments: [] as Array<{
        id: number,
        text: string,
        created_at: string,
        user_name: string
      }>
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
    this.loadCachedComments()
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
    cacheKey(): string {
      const pid = this.$route.params.id   as string
      const ex  = this.$route.query.left  as string
      return `comments_${pid}_${ex}`
    },
    loadCachedComments() {
      try {
        this.comments = JSON.parse(
          localStorage.getItem(this.cacheKey()) || '[]'
        )
      } catch {
        this.comments = []
      }
    },
    saveCommentsToCache(list: any[]) {
      localStorage.setItem(this.cacheKey(), JSON.stringify(list))
    },
    async fetchComments() {
      try {
        const res = await axios.get(
          `/v1/projects/${this.$route.params.id}/comments/`,
          { params: { example: this.$route.query.left } }
        )
        const list = (res.data.results || res.data).map((c: any) => ({
          id:         c.id,
          text:       c.text,
          created_at: c.created_at,
          user_name:  c.user?.username || c.username || 'Unknown'
        }))
        this.comments = list
        this.saveCommentsToCache(list)
      } catch {
        this.loadCachedComments()
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
    formatDate(dt: string): string {
      return new Date(dt).toLocaleString('en-US', {
        month: '2-digit',
        day:   '2-digit',
        year:  'numeric',
        hour:        '2-digit',
        minute:      '2-digit',
        hour12:      false
      })
    },
    async sendComment() {
      const text = this.commentText.trim()
      if (!text) return

      const localC = {
        id:         Date.now(),
        text,
        created_at: new Date().toISOString(),
        user_name:  this.currentUsername || 'Me'
      }
      this.comments.unshift(localC)
      this.saveCommentsToCache(this.comments)
      this.commentText = ''

      try {
        const { data } = await axios.post(
          `/v1/projects/${this.$route.params.id}/comments/`,
          { example: this.$route.query.left, text }
        )
        Object.assign(localC, {
          id:         data.id,
          created_at: data.created_at
        })
        this.saveCommentsToCache(this.comments)
      } catch (err) {
        console.warn('Não foi possível sincronizar:', err)
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
.comment-btn {
  width: 48px !important;
  height: 48px !important;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  right: 14px !important;
}

.comment-text {
  font-size: 0.45rem;
  line-height: 1;
  color: white;
  text-transform: uppercase;
  text-align: center;
  white-space: normal;
  word-break: break-word;
}
.cancel-btn {
  color: black !important;
  text-transform: none;
  justify-content: flex-start;
}

.comments-list {
  flex: 1;
  overflow-y: auto;
}

.form-container {
  flex-shrink: 0;
  padding: 0 16px 16px;
}
</style>