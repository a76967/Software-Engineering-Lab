import ApiService from '@/services/api.service'

export class APIRuleVoteRepository {
  private baseUrl(projectId: number): string {
    return `/projects/${projectId}/rule-votes/`
  }

  async create(
    projectId: number,
    payload: { grid: number; rule_index: number; value: string }
  ): Promise<void> {
    await ApiService.post(this.baseUrl(projectId), payload)
  }

  async list(projectId: number, grid: number): Promise<any[]> {
    const res = await ApiService.get(this.baseUrl(projectId), {
      params: { grid, limit: 1000 }
    })
    return res.data.results || res.data
  }
}