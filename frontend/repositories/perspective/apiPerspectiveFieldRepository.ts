import ApiService from '@/services/api.service'
import { PerspectiveField } from '@/domain/models/perspective/perspective-field'

export class APIPerspectiveFieldRepository {
  private baseUrl(projectId: number): string {
    return `/projects/${projectId}/perspective-items/`
  }

  async list(projectId: number): Promise<PerspectiveField[]> {
    const res = await ApiService.get(this.baseUrl(projectId))
    const data = res.data.results || res.data
    return data as PerspectiveField[]
  }

  async create(projectId: number, payload: any): Promise<PerspectiveField> {
    const res = await ApiService.post(this.baseUrl(projectId), payload)
    return res.data as PerspectiveField
  }
}