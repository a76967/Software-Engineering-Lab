export interface PerspectiveField {
  id?: number
  project: number
  name: string
  dataType: string
  required: boolean
  enum?: string[]
  order?: number
}