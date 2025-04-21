<template>
  <v-container fluid class="pa-0">
    <v-card class="mx-auto my-4 chat-card" max-width="800">
      
      <v-card-title class="chat-header">
        <v-icon left class="mr-2">mdi-chat-processing</v-icon>
        <span class="headline">Discuss about the project here!</span>
      </v-card-title>

      <v-card-text class="chat-window">
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['chat-message', msg.senderId === userId ? 'sent' : 'received']"
        >
          <div class="message-bubble">
            <div v-if="msg.senderId !== userId" class="message-sender">
              {{ msg.senderName }}
            </div>
            <div class="message-text">{{ msg.text }}</div>
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>
      </v-card-text>

      <v-card-actions class="chat-input-area">
        <v-text-field
          v-model="newMessage"
          placeholder="Type a message..."
          dense
          outlined
          rounded
          hide-details
          class="chat-input"
          @keyup.enter="newMessage.trim() && sendMessage()"
        />
        <v-btn fab small color="primary" dark @click="newMessage.trim()
        && sendMessage()">SEND</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import axios from 'axios'

interface ChatMessage {
  id: number
  text: string
  senderId: number
  senderName: string
  timestamp: string
}

export default defineComponent({
  layout: 'project',
  name: 'ChatWindow',
  data() {
    return {
      messages: [] as ChatMessage[],
      newMessage: '',
      userId: 0
    }
  },
  async created() {
    this.userId = Number(this.$store.getters['auth/userId'] || 0)
    await this.fetchMessages()
  },
  methods: {
    async fetchMessages() {
      try {
        const res = await axios.get<ChatMessage[]>(
          `/v1/projects/${this.$route.params.id}/discussions/`
        )
        this.messages = res.data
        this.$nextTick(this.scrollToBottom)
      } catch (e) {
        console.error('Failed to load discussions:', e)
      }
    },
    async sendMessage() {
      const text = this.newMessage.trim()
      if (!text) return
      try {
        const now = new Date().toISOString()
        this.messages.push({ id: Date.now(), text, senderId: this.userId, senderName: '', timestamp: now })
        this.newMessage = ''
        this.$nextTick(this.scrollToBottom)
        const res = await axios.post<ChatMessage>(
          `/v1/projects/${this.$route.params.id}/discussions/`,
          { text }
        )
        this.messages.splice(this.messages.findIndex(m => m.id === res.data.id), 1, res.data)
        this.$nextTick(this.scrollToBottom)
      } catch (e) {
        console.error('Failed to send message:', e)
      }
    },
    formatTime(ts: string) {
      return new Date(ts).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
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
  min-height: 0;
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

.chat-message.sent .message-bubble {
  background-color: #bcc0e0;
  border-radius: 20px 20px 4px 20px;
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

</style>