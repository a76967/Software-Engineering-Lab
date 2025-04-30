import ApiService from '@/services/api.service'
import { AnnotationRuleGrid } from '~/domain/models/annotation-rule/annotation-rule'

export class APIAnnotationRuleRepository {
  private baseUrl(projectId: number) {
    return `/projects/${projectId}/rule-grids`
  }

  async list(projectId: number): Promise<AnnotationRuleGrid[]> {
    const res = await ApiService.get(this.baseUrl(projectId))
    const data = res.data.results || res.data
    return data.map((item: any) => this.toModel(item))
  }

  async get(projectId: number, id: number): Promise<AnnotationRuleGrid> {
    const res = await ApiService.get(`${this.baseUrl(projectId)}/${id}`)
    return this.toModel(res.data)
  }

  async create(projectId: number, rules: string[]): Promise<AnnotationRuleGrid> {
    const res = await ApiService.post(this.baseUrl(projectId), { rules })
    return this.toModel(res.data)
  }

  async delete(projectId: number, id: number): Promise<void> {
    await ApiService.delete(`${this.baseUrl(projectId)}/${id}`)
  }

  private toModel(item: any): AnnotationRuleGrid {
    return new AnnotationRuleGrid(
      item.id,
      item.project,
      item.version,
      item.rules,
      item.created_by,
      item.last_edited_by,
      item.created_at,
      item.updated_at
    )
  }
}