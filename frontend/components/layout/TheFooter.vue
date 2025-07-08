<template>
  <v-footer v-show="showFooter" color="black" class="white--text text-center pa-4">
    <v-container>
      <v-row justify="space-between" align="center">
        <v-col cols="6" class="text-left">
          &copy; 2025 Doccana, Software Engineering Lab
        </v-col>
        <v-col cols="6" class="text-right d-flex align-center justify-end" style="gap: 16px">
          <span>Universidade do Algarve</span>
          <v-btn
            outlined
            style="color: white; margin-left: 0.5vw; border-color: white"
            @click="$router.push(localePath('/about'))"
          >
            About Us
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script>
export default {
  data() {
    return {
      showFooter: false,
      scrollContainer: null
    }
  },
  mounted() {
    // apanhar o elemento que efectivamente faz scroll (v-main)
    this.scrollContainer = document.querySelector('.v-application .v-main')
    if (this.scrollContainer) {
      this.scrollContainer.addEventListener('scroll', this.checkScroll)
      this.checkScroll()
    }
  },
  beforeDestroy() {
    if (this.scrollContainer) {
      this.scrollContainer.removeEventListener('scroll', this.checkScroll)
    }
  },
  methods: {
    checkScroll() {
      const el = this.scrollContainer
      const scrollTop    = el.scrollTop
      const viewHeight   = el.clientHeight
      const scrollHeight = el.scrollHeight
      // se o conteúdo for mais curto que a janela ou chegámos ao fim
      this.showFooter = scrollHeight <= viewHeight
        ? true
        : (scrollTop + viewHeight) >= (scrollHeight - 1)
    }
  }
}
</script>
