export const state = () => ({
  current: {},
  versions: [],
  isProjectAdmin: false
})

export const getters = {
  currentProject(state) {
    return state.current
  },

  project(state) {
    return state.current
  },

  projectVersions(state) {
    return state.versions
  },

  isProjectAdmin(state) {
    return state.isProjectAdmin
  }
}

export const mutations = {
  setCurrent(state, payload) {
    state.current = payload
  },
  setVersions(state, versions) {
    state.versions = versions
  },
  setProjectAdmin(state, isAdmin) {
    state.isProjectAdmin = isAdmin
  }
}

export const actions = {
  async setCurrentProject({ commit }, projectId) {
    try {
      const project = await this.$services.project.findById(projectId)
      commit('setCurrent', project)
      const member = await this.$repositories.member.fetchMyRole(projectId)
      commit('setProjectAdmin', member.isProjectAdmin)
      let versions = []
      if (member.isProjectAdmin) {
        versions = await this.$services.project.listVersions(projectId)
      }
      commit('setVersions', versions)
    } catch (error) {
      throw new Error(error)
    }
  },

  async createVersion({ dispatch, state }) {
    const newProject = await this.$services.project.createVersion(state.current.id)
    await dispatch('setCurrentProject', newProject.id)
    return newProject
  }
}