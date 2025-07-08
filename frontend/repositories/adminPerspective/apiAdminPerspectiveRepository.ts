import ApiService from '@/services/api.service'

export class APIAdminPerspectiveRepository {
  async list(projectId: number): Promise<any[]> {
    const res = await ApiService.get(`/projects/${projectId}/admin-perspectives/`)
    return res.data.results || res.data
  }

  async create(projectId: number, payload: any): Promise<any> {
    const res = await ApiService.post(`/projects/${projectId}/admin-perspectives/`, payload)
    return res.data
  }

  async delete(projectId: number, id: number): Promise<void> {
    await ApiService.delete(`/projects/${projectId}/admin-perspectives/${id}/`)
  }
}