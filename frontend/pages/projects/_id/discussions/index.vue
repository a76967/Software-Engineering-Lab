<template>
  <v-container fluid class="pa-0">
    <v-card class="mx-auto my-4 chat-card" max-width="800">
      <div class="session-bar primary white--text">
        <v-select
          v-model="activeSession"
          :items="sessions"
          item-text="text"
          item-value="value"
          label="Session"
          dense
          hide-details
          outlined
          dark
          color="white"
          item-color="white"
          class="me-2 white--text session-select"
          @change="onSessionChange"
        />
        <!-- only admins see Add Session -->
        <v-btn
          v-if="isProjectAdmin"
          small
          outlined
          color="white"
          class="ms-2"
          @click="addSession"
        >
          Add Session
        </v-btn>
        <v-chip
          small
          class="ms-2 white--text"
          :color="isLatestSession ? 'green' : 'red'"
        >
          {{ isLatestSession ? 'ON GOING' : 'READ ONLY' }}
        </v-chip>
      </div>

      <v-card-title class="chat-header">
        <v-icon left class="mr-2">mdi-chat-processing</v-icon>
        <span class="headline">Discuss about the annotation rules here!</span>
      </v-card-title>

      <v-alert
        v-if="error"
        type="error"
        dense
        class="mx-4 mt-4"
      >
        {{ error }}
      </v-alert>

      <v-card-text class="chat-window">
        <template v-if="!messages.length">
          <div class="no-messages">
            No discussions yet..
          </div>
        </template>
        <template v-else>
          <div
            v-for="msg in messages"
            :key="msg.id"
            :class="{
              'chat-message': true,
              'sent':    msg.senderId === userId,
              'received': msg.senderId !== userId
            }"
          >
            <div class="message-bubble">
              <div v-if="msg.senderId !== userId" class="message-sender">
                {{ msg.senderName }}
              </div>
              <div class="message-text">{{ msg.text }}</div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>
        </template>
      </v-card-text>

      <v-card-actions
        v-if="isLatestSession"
        class="chat-input-area"
      >
        <v-text-field
          v-model="newMessage"
          placeholder="Type a message.."
          dense
          outlined
          rounded
          hide-details
          class="chat-input"
          @keyup.enter="newMessage.trim() && sendMessage()"
        />
        <v-btn
          fab
          small
          color="primary"
          dark
          class="ms-2"
          @click="newMessage.trim() && sendMessage()"
        >
          SEND
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import axios from 'axios'
import { discussionRepository } from '~/repositories/apiDiscussionRepository'
import { DiscussionSession } from '~/domain/models/discussion/DiscussionSession'

interface ChatMessage {
  id: number
  text: string
  senderId: number
  senderName: string
  timestamp: string
  session: number
}

export default Vue.extend({
  layout: 'project',
  name: 'DiscussionsPage',
  data() {
    return {
      messages: [] as ChatMessage[],
      newMessage: '',
      sessions: [] as Array<{ value: number; text: string }>,
      activeSession: 1,
      userId: 0,
      error: ''
    }
  },
  computed: {
    ...mapGetters('projects', ['isProjectAdmin']),
    latestSession(): number {
      return this.sessions.length ? Math.max(...this.sessions.map(x => x.value)) : 1
    },
    isLatestSession(): boolean {
      return this.activeSession === this.latestSession
    }
  },
  async mounted() {
    this.userId = Number(this.$store.getters['auth/getUserId'] || 0)
    console.log('🟢 current userId =', this.userId)
    // ensure at least one session exists, then select it
    await this.fetchSessions()
    await this.fetchMessages(this.activeSession)
  },
  methods: {
    async fetchSessions() {
      try {
        const projectId = Number(this.$route.params.id)
        // load existing sessions
        let list = await discussionRepository.listSessions(projectId)
        // if none exist, auto-create session #1
        if (!list.length) {
          await discussionRepository.createSession(projectId)
          list = await discussionRepository.listSessions(projectId)
        }
        this.sessions = list.map((s: DiscussionSession) => ({
          value: s.number,
          text: `#${s.number}`
        }))
        this.activeSession = this.sessions
          .some(x => x.value === this.activeSession)
          ? this.activeSession
          : this.sessions[this.sessions.length - 1].value
      } catch (err) {
        console.error('❌ fetchSessions failed:', err)
        this.sessions = [{ value: 1, text: '#1' }]
        this.activeSession = 1
      }
    },

    async fetchMessages(session: number) {
      this.error = ''
      try {
        const projectId = Number(this.$route.params.id)
        const raw = await discussionRepository.list(projectId, session)
        this.messages = raw.map(m => ({
          id:         m.id,
          text:       m.text,
          senderId:   Number(m.senderId),
          senderName: m.senderName,
          timestamp:  m.timestamp,
          session:    m.session
        }))
      } catch (err) {
        console.error('❌ fetchMessages failed:', err)
        this.messages = []
        this.error = "Error: Can't access our database!"
      }
      this.$nextTick(this.scrollToBottom)
    },

    async sendMessage() {
      if (!this.isLatestSession) return
      this.error = ''
      const text = this.newMessage.trim()
      if (!text) return
      this.newMessage = ''
      try {
        axios.defaults.withCredentials = true
        const projectId = Number(this.$route.params.id)
        await discussionRepository.create(projectId, text, this.activeSession)
        await this.fetchMessages(this.activeSession)
      } catch (err) {
        console.error('❌ sendMessage failed:', err)
        this.error = "Error: Can't access our database!"
      }
    },
    async addSession () {
      try {
        const projectId = Number(this.$route.params.id)
        // create a new session (auto-numbered by backend)
        const newSession = await discussionRepository.createSession(projectId)
        // reload and switch to that session
        await this.fetchSessions()
        this.switchSession(newSession.number)
      } catch (err) {
        console.error('❌ addSession failed:', err)
      }
    },
    switchSession(s: number) {
      this.activeSession = s
      this.messages = []
      this.fetchMessages(s)
    },
    onSessionChange(val: number) {
      this.switchSession(val)
    },
    formatTime(ts: string) {
      return new Date(ts).toLocaleString('en-US', {
        day:   '2-digit',
        month: '2-digit',
        year:  'numeric',
        hour:   '2-digit',
        minute: '2-digit',
        hour12: false
      })
    },
    scrollToBottom() {
      const el = this.$el.querySelector('.chat-window') as HTMLElement
      if (el) el.scrollTop = el.scrollHeight
    }
  }
})
</script>

<style scoped>
.chat-card {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  border-radius: 12px;
  overflow: hidden;
  background-color: #ece5dd;
}
.session-bar {
  display: flex;
  align-items: center;
  padding: 8px;
}
.chat-header {
  background-color: #6376ab;
  color: #ffffff;
  font-weight: 500;
  justify-content: center;
  position: sticky;
  top: 0;
  z-index: 2;
}
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #ece5dd;
}
.chat-message {
  display: flex;
  margin-bottom: 12px;
}
.chat-message.sent {
  justify-content: flex-end;
}
.chat-message.received {
  justify-content: flex-start;
}
.message-bubble {
  max-width: 75%;
  padding: 10px 14px;
  background-color: #ffffff;
  border-radius: 20px 20px 20px 4px;
}
.chat-message.sent .message-bubble {
  background-color: #bcc0e0;
  border-radius: 20px 20px 4px 20px;
}
.message-sender {
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: rgba(0, 0, 0, 0.6);
}
.message-text {
  white-space: pre-wrap;
  word-break: break-word;
}
.message-time {
  font-size: 0.7rem;
  color: rgba(0, 0, 0, 0.45);
  margin-top: 6px;
  text-align: right;
}
.chat-input-area {
  background-color: #f0f0f0;
  border-top: 1px solid #ddd;
  padding: 8px 16px;
  position: sticky;
  bottom: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8px;
}
.chat-input {
  background-color: #ffffff !important;
  border-radius: 50px;
}

.theme--dark .chat-card {
  background-color: #2a2a2e !important;
}
.theme--dark .chat-window {
  background-color: #2a2a2e !important;
}
.theme--dark .message-bubble {
  background-color: #44464f !important;
}
.theme--dark .chat-message.sent .message-bubble {
  background-color: #57578c !important;
}
.theme--dark .message-sender {
  color: rgba(255, 255, 255, 0.7) !important;
}
.theme--dark .message-text {
  color: #e0e0e0 !important;
}
.theme--dark .message-time {
  color: rgba(255, 255, 255, 0.5) !important;
}
.theme--dark .chat-input-area {
  background-color: #3c3c3f !important;
  border-top-color: #555 !important;
}
.theme--dark .chat-input {
  background-color: #424245 !important;
}
.theme--dark .session-bar {
  background-color: #3c3c3f;
}
</style>