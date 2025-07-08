import ApiService from '@/services/api.service'

export class APIGridVoteRepository {
  private baseUrl(projectId: number): string {
    return `/projects/${projectId}/grid-votes/`
  }

  async create(projectId: number, payload: { grid: number }): Promise<void> {
    await ApiService.post(this.baseUrl(projectId), payload)
  }

  async list(projectId: number, grid?: number): Promise<any[]> {
    const params = grid
      ? { params: { grid, limit: 1000 } }
      : { params: { limit: 1000 } }
    const res = await ApiService.get(this.baseUrl(projectId), params)
    return res.data.results || res.data
  }
}