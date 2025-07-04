<template>
  <v-container fluid class="pa-0">
    <v-card class="mx-auto my-4 chat-card" max-width="800">
      <div class="session-bar">
        <!-- dropdown to pick a session -->
        <v-select
          v-model="activeSession"
          :items="sessions"
          label="Session"
          dense
          hide-details
          outlined
          class="me-2"
          @change="fetchMessages(activeSession)"
        />
        <!-- add-new-session button -->
        <v-btn
          color="primary"
          dark
          small
          @click="addSession"
          elevation="2"
          class="white--text"
          rounded
          tile
        >
          <v-icon left small>mdi-plus</v-icon>
          Add Session
        </v-btn>
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

      <v-card-actions class="chat-input-area">
        <v-text-field
          v-model="newMessage"
          placeholder="Type a message.."
          dense
          outlined
          rounded
          hide-details
          class="chat-input"
          @keyup.enter="newMessage.trim() && sendMessage()"
        ></v-text-field>
        <v-btn fab small color="primary" dark @click="newMessage.trim() && sendMessage()">
          SEND
        </v-btn>
    </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
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
      sessions: [] as number[],
      activeSession: 1,
      userId: 0,
      error: ''
    }
  },
  async mounted() {
    this.userId = Number(this.$store.getters['auth/getUserId'] || 0)
    console.log('🟢 current userId =', this.userId)
    await this.fetchSessions()
    await this.fetchMessages(this.activeSession)
  },
  computed: {
    validMessages(): ChatMessage[] {
      return this.messages
    }
  },
  methods: {
    async fetchSessions() {
      try {
        const projectId = Number(this.$route.params.id)
        const list = await discussionRepository.listSessions(projectId)
        this.sessions = list.map((s: DiscussionSession) => s.number)
        if (!this.sessions.includes(this.activeSession)) {
          this.activeSession = this.sessions[0] || 1
        }
      } catch (err) {
        console.error('❌ fetchSessions failed:', err)
        this.sessions = [1]
      }
    },
    async fetchMessages(session: number) {
      this.error = ''
      console.log('🔄 fetching discussions…')
      try {
        const projectId = Number(this.$route.params.id)
        const raw = await discussionRepository.list(projectId, session)
        this.messages = raw.map(m => ({
          ...m,
          senderId: Number(m.senderId)
        }))
        console.log('💬 loaded messages:', this.messages.map(m => m.senderId))
      } catch (err) {
        console.error('❌ fetchMessages failed:', err)
        this.messages = []
        this.error = "Error: Can't access our database!"
      }
      this.$nextTick(this.scrollToBottom)
      console.log('✅ got', this.messages.length, 'messages')
    },
    async sendMessage() {
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

        // if there are **no** sessions yet, quietly create #1
        if (!this.sessions.length) {
          await discussionRepository.createSession(projectId)
        }

        // now create the *next* number
        const session = await discussionRepository.createSession(projectId)

        // fetch the authoritative list instead of pushing manually
        await this.fetchSessions()
        this.switchSession(session.number)
      } catch (err) {
        console.error('❌ addSession failed:', err)
      }
    },
    switchSession(s: number) {
      this.activeSession = s
      this.messages = []
      this.fetchMessages(s)
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