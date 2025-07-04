import ApiService from '@/services/api.service'

export class APICountryRepository {
  async list(): Promise<string[]> {
    const res = await ApiService.get('/countries/')
    return res.data as string[]
  }
}