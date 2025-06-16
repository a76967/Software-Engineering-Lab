<template>
  <v-card>
    <v-alert v-if="dbError" type="error" dense>
      {{ dbError }}
    </v-alert>

    <v-card-text>
      <v-form ref="form" v-model="isValid" lazy-validation>
        <v-select
          class="custom-input"
          v-model="form.category"
          :items="categories"
          :label="$t('Category')"
          required
          :rules="[v => !!v || 'Categoria obrigatória']"
        />
        <v-textarea
          class="custom-input"
          v-model="form.text"
          :label="$t('Text')"
          counter="2000"
          required
          rows="10"
          auto-grow
          :rules="[v => !!v || 'Texto obrigatório']"
        />
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn text @click="goBack">{{ $t('generic.cancel') }}</v-btn>
      <v-btn color="primary" :disabled="!isValid" @click="submitPerspective">
        {{ $t('generic.add') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'

export default Vue.extend({
  name: 'CreatePerspective',
  layout: 'project',
  data() {
    return {
      form: {
        text: '',
        category: 'subjective'
      },
      categories: [
        { text: this.$t('Cultural'), value: 'cultural' },
        { text: this.$t('Technic'), value: 'technic' },
        { text: this.$t('Subjective'), value: 'subjective' }
      ],
      isValid: false,
      dbError: ""
    }
  },
  computed: {
    ...mapGetters('auth', ['getUsername']),
    userRole(): string {
      return this.$store.state.auth.role || 'annotator'
    }
  },
  methods: {
    async submitPerspective() {
      if (!(this.$refs.form as any).validate()) {
        return
      }
      const projectId = Number(this.$route.params.id)
      const userId = this.$store.state.auth.id
      if (!userId) {
        console.error('User ID is missing.')
        return
      }
      const payload: any = {
        text: this.form.text,
        category: this.form.category,
        user: userId,
        project: projectId,
        roleOverride: true,
        role: this.userRole
      }
      try {
        await this.$repositories.perspective.create(projectId, payload)
        this.$router.push({
          path: this.localePath('/message'),
          query: {
            message: 'Perspective added successfully!',
            redirect: this.localePath(`/projects/${projectId}/perspectives`)
          }
        })
      } catch (error: any) {
        console.error(error)
        this.dbError = "Can't access our database!"
      }
    },
    goBack() {
      this.$router.push(this.localePath(`/projects/${this.$route.params.id}/perspectives`))
    }
  }
})
</script>

<style scoped>
.v-card {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.headline {
  cursor: pointer;
  font-weight: bold;
  font-size: 1.5rem;
  display: inline-flex;
  align-items: center;
}

.headline .edit-icon {
  opacity: 0;
  transition: opacity 0.3s;
  color: inherit;
  margin-left: 8px;
}

.headline:hover .edit-icon {
  opacity: 1;
}

::v-deep .custom-input .v-input__slot {
  background-color: #f0f0f0 !important;
  border-radius: 4px;
}
</style>