<script lang="ts">
import Vue from 'vue'
import { VDataTable, VProgressCircular, VIcon, VBtn, VTextField } from 'vuetify/lib'

interface Row {
  id: number
  snippet: string
  LA: number
  ABSTENTION: number
  LD: number
  LE: number
  LF: number
  LB: number
  X: number
  LC: number
}

export default Vue.extend({
  name: 'DiffsPage',
  components: { VDataTable, VProgressCircular, VIcon, VBtn, VTextField },
  data () {
    return {
      search: '',
      rows: [
        {
          id: 1,
          snippet: 'Test message 1',
          LA: 2,
          ABSTENTION: 1,
          LD: 1,
          LE: 1,
          LF: 0,
          LB: 0,
          X: 0,
          LC: 0
        },
        {
          id: 2,
          snippet: 'Another test message',
          LA: 2,
          ABSTENTION: 0,
          LD: 0,
          LE: 0,
          LF: 2,
          LB: 2,
          X: 0,
          LC: 0
        },
        {
          id: 3,
          snippet: 'Short msg',
          LA: 1,
          ABSTENTION: 0,
          LD: 1,
          LE: 1,
          LF: 1,
          LB: 1,
          X: 1,
          LC: 1
        },
        {
          id: 4,
          snippet: 'Yet another test message',
          LA: 2,
          ABSTENTION: 2,
          LD: 0,
          LE: 0,
          LF: 0,
          LB: 1,
          X: 0,
          LC: 1
        }
      ] as Row[],
      headers: [
        { text: 'Snippet', value: 'snippet', width: '200' },
        { text: 'LA', value: 'LA' },
        { text: 'ABSTENTION', value: 'ABSTENTION' },
        { text: 'LD', value: 'LD' },
        { text: 'LE', value: 'LE' },
        { text: 'LF', value: 'LF' },
        { text: 'LB', value: 'LB' },
        { text: 'X', value: 'X' },
        { text: 'LC', value: 'LC' },
        { text: 'Total', value: 'total', sortable: false },
        { text: 'Agreement', value: 'agreement', sortable: false },
        { text: 'Compare', value: 'compare', sortable: false },
        { text: 'Discussion', value: 'discussion', sortable: false },
        { text: 'disagreement', value: 'disagreement', sortable: false }
      ]
    }
  },
  computed: {
    filtered (): Row[] {
      if (!this.search) return this.rows
      return this.rows.filter(r => r.snippet.toLowerCase().includes(this.search.toLowerCase()))
    }
  },
  methods: {
    getRowClass (item: Row) {
      return this.agreementPercent(item) < 50 ? 'low-agreement' : '';
    },
    rowTotal (r: Row) {
      const { LA, ABSTENTION, LD, LE, LF, LB, X, LC } = r
      return LA + ABSTENTION + LD + LE + LF + LB + X + LC
    },
    agreementPercent (r: Row) {
      const total = this.rowTotal(r)
      if (total === 0) return 0
      const votes = [r.LA, r.ABSTENTION, r.LD, r.LE, r.LF, r.LB, r.X, r.LC]
      const majority = Math.max(...votes)
      return Math.round((majority / total) * 100)
    },
    onCompare (r: Row) { this.$router.push(`/compare/${r.id}`) },
    onDiscussion (r: Row) { this.$router.push(`/discussion/${r.id}`) }
  }
})
</script>

<template>
  <v-card flat>
    <v-card-title class="d-flex align-center">
      <span class="headline mr-4">Disagreements</span>
      <v-spacer />
      <v-text-field
        v-model="search"
        dense
        hide-details
        append-icon="mdi-magnify"
        label="Search"
      disable-pagination
      hide-default-footer
      ></v-text-field>
    </v-card-title>
      <template #item.total="{ item }">{{ rowTotal(item) }}</template>

      <template #item.agreement="{ item }">
        <div class="d-flex justify-center align-center">
          <v-progress-circular
            :value="agreementPercent(item)"
            :size="34"
            :width="4"
            color="primary"
          >
            <small>{{ agreementPercent(item) }}%</small>
          </v-progress-circular>
        </div>
      </template>

      <template #item.compare="{ item }">
        <v-btn icon small @click="onCompare(item)">
          <v-icon>mdi-eye-outline</v-icon>
        </v-btn>
      </template>

      <template #item.discussion="{ item }">
        <v-btn icon small @click="onDiscussion(item)">
          <v-icon>mdi-comment-outline</v-icon>
        </v-btn>
      </template>

      <template #item.disagreement="{ item }">
        <v-icon color="warning" small>mdi-alert</v-icon>
      </template>

      <template #item.snippet="{ item }">
        <span style="max-width:180px; display:inline-block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{{ item.snippet }}</span>
      </template>
    </v-data-table>
  </v-card>
</template>

<style scoped>
tr.v-data-table__tr {
  transition: background 0.2s;
}
tr.low-agreement {
  background-color: rgba(255, 0, 0, 0.15) !important;
}
</style>