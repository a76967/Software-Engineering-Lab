import axios from 'axios'
import { Discussion } from '~/domain/models/discussion/Discussion'

export const discussionRepository = {
  async list(projectId: number): Promise<Discussion[]> {
    const res = await axios.get<Discussion[]>(`/v1/projects/${projectId}/discussions/`)
    return res.data
  },

  async create(projectId: number, text: string): Promise<Discussion> {
    const res = await axios.post<Discussion>(`/v1/projects/${projectId}/discussions/`, { text })
    return res.data
  },

  async delete(projectId: number, discussionId: number): Promise<void> {
    await axios.delete(`/v1/projects/${projectId}/discussions/${discussionId}/`)
  }
}