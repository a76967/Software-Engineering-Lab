import axios from 'axios'
import { Discussion } from '~/domain/models/discussion/Discussion'

axios.defaults.withCredentials = true

export const discussionRepository = {
  async list(projectId: number): Promise<Discussion[]> {
    const res = await axios.get<{
      count: number
      next: string | null
      previous: string | null
      results: Discussion[]
    }>(`/v1/projects/${projectId}/discussions/`)
    return res.data.results || []
  },

  async create(projectId: number, text: string): Promise<Discussion> {
    const res = await axios.post<Discussion>(
      `/v1/projects/${projectId}/discussions/`,
      { text }
    )
    return res.data
  }
}