<template>
  <!-- desativa a validação de “.” em v-slot só aqui -->
  <!-- eslint-disable vue/valid-v-slot -->
  <v-data-table
    :value="value"
    :headers="headers"
    :items="items"
    :search="search"
    :loading="isLoading"
    item-key="id"
    show-select
    @input="$emit('input', $event)"
  >
    <!-- slot de pesquisa -->
    <template #top>
      <v-text-field
        v-model="search"
        :prepend-inner-icon="mdiMagnify"
        :label="$t('generic.search')"
        single-line
        hide-details
        filled
      />
    </template>

    <!-- coluna role -->
    <template #item.rolename="{ item }">
      {{ $translateRole(item.rolename, rolesMap) }}
    </template>

    <!-- coluna ações -->
    <template #item.actions="{ item }">
      <v-icon small @click="$emit('edit', item)">{{ mdiPencil }}</v-icon>
    </template>

    <!-- coluna vote -->
    <template #item.vote="{ item }">
      <span v-if="item.vote != null">v{{ item.vote }}</span>
      <v-icon v-else small color="grey">mdi-close</v-icon>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiMagnify, mdiPencil } from '@mdi/js'

export default Vue.extend({
  props: {
    isLoading: { type: Boolean, default: false, required: true },
    items:     { type: Array as () => any[], default: () => [], required: true },
    value:     { type: Array as () => any[], default: () => [], required: true }
  },
  data() {
    return {
      search: '',
      mdiMagnify,
      mdiPencil
    }
  },
  computed: {
    headers() {
      return [
        { text: this.$t('generic.name'),    value: 'username' },
        { text: this.$t('members.role'),    value: 'rolename' },
        { text: this.$t('generic.actions'), value: 'actions', sortable: false },
        { text: 'Vote',                     value: 'vote',    align: 'center' }
      ]
    },
    rolesMap(): Record<string,string> {
      // forçar o retorno de objecto e converter de forma segura
      const obj = this.$i18n.t(
        'members.roles',
        this.$i18n.locale,
        { returnObjects: true }
      )
      return (obj as unknown) as Record<string,string>
    }
  }
})
</script>
