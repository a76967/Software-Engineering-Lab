import { Plugin } from '@nuxt/types'
import { APIAuthRepository } from '@/repositories/auth/apiAuthRepository'
import { APIUserRepository } from '@/repositories/user/apiUserRepository'
import { APIPerspectiveRepository } from '@/repositories/perspective/apiPerspectiveRepository'
import { APIPerspectiveFieldRepository } from '@/repositories/perspective/apiPerspectiveFieldRepository'
import { APIAdminPerspectiveRepository } from '@/repositories/adminPerspective/apiAdminPerspectiveRepository'
import { APIProjectRepository } from '@/repositories/project/apiProjectRepository'
import { APIMemberRepository } from '@/repositories/member/apiMemberRepository'
import { APIRoleRepository } from '@/repositories/role/apiRoleRepository'
import { APITagRepository } from '@/repositories/tag/apiTagRepository'
import { APIExampleRepository } from '@/repositories/example/apiDocumentRepository'
import { APICommentRepository } from '@/repositories/comment/apiCommentRepository'
import { APITaskStatusRepository } from '@/repositories/celery/apiTaskStatusRepository'
import { APIMetricsRepository } from '@/repositories/metrics/apiMetricsRepository'
import { LocalStorageOptionRepository } from '@/repositories/option/apiOptionRepository'
import { APIAssignmentRepository } from '@/repositories/example/apiAssignmentRepository'
import { APIConfigRepository } from '@/repositories/autoLabeling/config/apiConfigRepository'
import { APITemplateRepository } from '@/repositories/autoLabeling/template/apiTemplateRepository'
import { APICatalogRepository } from '@/repositories/upload/apiCatalogRepository'
import { APIParseRepository } from '@/repositories/upload/apiParseRepository'
import { APIDownloadFormatRepository } from '@/repositories/download/apiDownloadFormatRepository'
import { APIDownloadRepository } from '@/repositories/download/apiDownloadRepository'
import { APILabelRepository } from '@/repositories/label/apiLabelRepository'
import { APICategoryRepository } from '@/repositories/tasks/apiCategoryRepository'
import { APISpanRepository } from '@/repositories/tasks/apiSpanRepository'
import { APIRelationRepository } from '@/repositories/tasks/apiRelationRepository'
import { APITextLabelRepository } from '@/repositories/tasks/apiTextLabelRepository'
import { APIBoundingBoxRepository } from '@/repositories/tasks/apiBoundingBoxRepository'
import { APISegmentationRepository } from '~/repositories/tasks/apiSegmentationRepository'
import { APICountryRepository } from '@/repositories/country/apiCountryRepository'

export interface Repositories {
  // Auth
  auth: APIAuthRepository
  user: APIUserRepository

  // Perspectives
  perspective: APIPerspectiveRepository
  perspectiveField: APIPerspectiveFieldRepository
  adminPerspective: APIAdminPerspectiveRepository

  // Projects & members
  project: APIProjectRepository
  member: APIMemberRepository
  role: APIRoleRepository
  tag: APITagRepository

  // Examples & comments
  example: APIExampleRepository
  comment: APICommentRepository
  taskStatus: APITaskStatusRepository
  metrics: APIMetricsRepository

  // UI options
  option: LocalStorageOptionRepository
  assignment: APIAssignmentRepository

  // Auto-labeling
  config: APIConfigRepository
  template: APITemplateRepository

  // Upload
  catalog: APICatalogRepository
  parse: APIParseRepository

  // Download
  downloadFormat: APIDownloadFormatRepository
  download: APIDownloadRepository

  // Label types
  categoryType: APILabelRepository
  spanType: APILabelRepository
  relationType: APILabelRepository

  // Task-specific annotation repos
  category: APICategoryRepository
  span: APISpanRepository
  relation: APIRelationRepository
  textLabel: APITextLabelRepository
  boundingBox: APIBoundingBoxRepository
  segmentation: APISegmentationRepository
  country: APICountryRepository
}

declare module 'vue/types/vue' {
  interface Vue {
    readonly $repositories: Repositories
  }
}

const repositories: Repositories = {
  auth: new APIAuthRepository(),
  user: new APIUserRepository(),

  // Perspectives
  perspective: new APIPerspectiveRepository(),
  perspectiveField: new APIPerspectiveFieldRepository(),
  adminPerspective: new APIAdminPerspectiveRepository(),

  // Projects & members
  project: new APIProjectRepository(),
  member: new APIMemberRepository(),
  role: new APIRoleRepository(),
  tag: new APITagRepository(),

  // Examples & comments
  example: new APIExampleRepository(),
  comment: new APICommentRepository(),
  taskStatus: new APITaskStatusRepository(),
  metrics: new APIMetricsRepository(),

  // UI options
  option: new LocalStorageOptionRepository(),
  assignment: new APIAssignmentRepository(),

  // Auto-labeling
  config: new APIConfigRepository(),
  template: new APITemplateRepository(),

  // Upload
  catalog: new APICatalogRepository(),
  parse: new APIParseRepository(),

  // Download
  downloadFormat: new APIDownloadFormatRepository(),
  download: new APIDownloadRepository(),

  // Label types
  categoryType: new APILabelRepository('category-type'),
  spanType: new APILabelRepository('span-type'),
  relationType: new APILabelRepository('relation-type'),

  // Task repos
  category: new APICategoryRepository(),
  span: new APISpanRepository(),
  relation: new APIRelationRepository(),
  textLabel: new APITextLabelRepository(),
  boundingBox: new APIBoundingBoxRepository(),
  segmentation: new APISegmentationRepository(),
  country: new APICountryRepository()
}

const plugin: Plugin = (_, inject) => {
  inject('repositories', repositories)
}

export default plugin
export { repositories }
