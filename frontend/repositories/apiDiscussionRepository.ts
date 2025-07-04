import axios from 'axios'
import { Discussion } from '~/domain/models/discussion/Discussion'
import { DiscussionSession } from '~/domain/models/discussion/DiscussionSession'

axios.defaults.withCredentials = true

export const discussionRepository = {
  async list(projectId: number, session: number): Promise<Discussion[]> {
    const res = await axios.get<{
      count: number
      next: string | null
      previous: string | null
      results: Discussion[]
    }>(`/v1/projects/${projectId}/discussions/?session=${session}`)
    return res.data.results || []
  },

  async create(projectId: number, text: string, session: number): Promise<Discussion> {
    const res = await axios.post<Discussion>(
      `/v1/projects/${projectId}/discussions/?session=${session}`,
      { text, session }
    )
    return res.data
  },

  async listSessions(projectId: number): Promise<DiscussionSession[]> {
    const res = await axios.get(
      `/v1/projects/${projectId}/discussion-sessions/`
    )
    const data = res.data
    // if the server is not paginated, `data` is already an array
    return Array.isArray(data) ? data : data.results || []
  },

  async createSession(projectId: number): Promise<DiscussionSession> {
    const res = await axios.post<DiscussionSession>(
      `/v1/projects/${projectId}/discussion-sessions/`
    )
    return res.data
  }
}