export const state = () => ({
  current: {},
  versions: []
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
  }
}

export const mutations = {
  setCurrent(state, payload) {
    state.current = payload
  },
  setVersions(state, versions) {
    state.versions = versions
  }
}

export const actions = {
  async setCurrentProject({ commit }, projectId) {
    try {
      const project = await this.$services.project.findById(projectId)
      commit('setCurrent', project)
      const versions = await this.$services.project.listVersions(projectId)
      commit('setVersions', versions)
    } catch (error) {
      throw new Error(error)
    }
  },

  async createVersion({ dispatch, state }) {
    const newProject = await this.$services.project.createVersion(state.current.id)
    await dispatch('setCurrentProject', newProject.id)
  }
}