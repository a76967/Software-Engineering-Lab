<template>
  <v-app>
    <the-header/>
    <v-main class="fill-height">
      <v-container fluid fill-height>
        <nuxt/>
      </v-container>
    </v-main>
    <!-- footer só “cola” no fim se não houver conteúdo suficiente -->
    <the-footer app/>
  </v-app>
</template>

<script>
import TheHeader from '~/components/layout/TheHeader'
import TheFooter from '~/components/layout/TheFooter'

export default {
  components: {
    TheHeader,
    TheFooter
  }
}
</script>
