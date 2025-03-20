<template>
  <v-app>
    <v-container fluid fill-height class="d-flex align-center justify-center">
      <v-row align="center" justify="center">
        <v-col cols="12" md="6" class="text-center">
          <v-card class="pa-6" outlined>
            <h1 class="display-2 primary--text mb-4">{{ msg }}</h1>
            <p class="headline">
              Redirecting in {{ countdown }} second<span v-if="countdown !== 1">s</span>..
            </p>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
export default {
  name: 'message',
  data() {
    return {
      countdown: Number(this.$route.query.duration) || 3
    }
  },
  computed: {
    msg() {
      return this.$route.query.message || 'Operation successful!';
    },
    redirectPath() {
      return this.$route.query.redirectPath || '/';
    }
  },
  mounted() {
    const intervalId = setInterval(() => {
      this.countdown--;
      if (this.countdown < 1) {
        clearInterval(intervalId);
        this.$router.push(this.redirectPath);
      }
    }, 1000);
  }
};
</script>

<style scoped>
.v-card {
  background-color: var(--v-background-base) !important;
}
</style>