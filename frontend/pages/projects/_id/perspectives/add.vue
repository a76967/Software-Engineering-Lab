<template>
  <v-card>
    <v-alert v-if="dbError" type="error" dense>
      {{ dbError }}
    </v-alert>

    <v-card-text>
      <v-form ref="form" v-model="isValid" lazy-validation>

        <v-menu
          ref="dobMenu"
          v-model="dobMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          min-width="290"
        >
          <template #activator="{ on, attrs }">
            <v-text-field
              v-model="form.dob"
              label="Birthday"
              readonly
              v-bind="attrs"
              v-on="on"
              required
            />
          </template>
          <v-date-picker
            v-model="form.dob"
            :max="today"
            :min="minDOB"
            @input="dobMenu = false"
            locale="en"
          />
        </v-menu>

        <v-select
          v-model="form.gender"
          :items="genders"
          label="Gender"
          required
        />

        <v-select
          v-model="form.nationality"
          :items="sortedCountries"
          label="Nationality (optional)"
          clearable
          autocomplete
        />

        <v-select
          v-model="form.category"
          :items="categories"
          label="Category"
          required
          class="bold-label"
        />

        <v-textarea
          class="custom-input"
          v-model="form.text"
          :label="$t('Text')"
          counter="2000"
          rows="10"
          auto-grow
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

const DEMONYMS: Record<string, string> = {
  Afghanistan: 'Afghan',
  Albania: 'Albanian',
  Algeria: 'Algerian',
  'American Samoa': 'American Samoan',
  Andorra: 'Andorran',
  Angola: 'Angolan',
  Anguilla: 'Anguillan',
  Antarctica: 'Antarctic',
  'Antigua and Barbuda': 'Antiguan, Barbudan',
  Argentina: 'Argentinian',
  Armenia: 'Armenian',
  Aruba: 'Aruban',
  Australia: 'Australian',
  Austria: 'Austrian',
  Azerbaijan: 'Azerbaijani',
  Bahamas: 'Bahamian',
  Bahrain: 'Bahraini',
  Bangladesh: 'Bangladeshi',
  Barbados: 'Barbadian',
  Belarus: 'Belarusian',
  Belgium: 'Belgian',
  Belize: 'Belizean',
  Benin: 'Beninese',
  Bermuda: 'Bermudian',
  Bhutan: 'Bhutanese',
  Bolivia: 'Bolivian',
  'Bonaire Sint Eustatius and Saba': 'Bonairean',
  'Bosnia and Herzegovina': 'Bosnian, Herzegovinian',
  Botswana: 'Botswanan',
  'Bouvet Island': 'Bouvet Islander',
  Brazil: 'Brazilian',
  'British Indian Ocean Territory': 'British Indian Ocean Territory nationality',
  'Brunei Darussalam': 'Bruneian',
  Bulgaria: 'Bulgarian',
  'Burkina Faso': 'Burkinabe',
  Burundi: 'Burundian',
  'Cabo Verde': 'Cabo Verdean',
  Cambodia: 'Cambodian',
  Cameroon: 'Cameroonian',
  Canada: 'Canadian',
  'Cayman Islands': 'Caymanian',
  'Central African Republic': 'Central African',
  Chad: 'Chadian',
  Chile: 'Chilean',
  China: 'Chinese',
  'Christmas Island': 'Christmas Islander',
  'Cocos Keeling Islands': 'Cocos Islander',
  Colombia: 'Colombian',
  Comoros: 'Comoran',
  Congo: 'Congolese',
  'Congo Democratic Republic of the': 'Congolese',
  'Cook Islands': 'Cook Islander',
  'Costa Rica': 'Costa Rican',
  "Côte d’Ivoire": 'Ivorian',
  Croatia: 'Croatian',
  Cuba: 'Cuban',
  Curaçao: 'Curaçaoan',
  Cyprus: 'Cypriot',
  Czechia: 'Czech',
  Denmark: 'Danish',
  Djibouti: 'Djiboutian',
  Dominica: 'Dominican',
  'Dominican Republic': 'Dominican',
  Ecuador: 'Ecuadorian',
  Egypt: 'Egyptian',
  'El Salvador': 'Salvadoran',
  'Equatorial Guinea': 'Equatorial Guinean',
  Eritrea: 'Eritrean',
  Estonia: 'Estonian',
  Eswatini: 'Swazi',
  Ethiopia: 'Ethiopian',
  'Falkland Islands': 'Falkland Islander',
  'Faroe Islands': 'Faroese',
  Fiji: 'Fijian',
  Finland: 'Finnish',
  France: 'French',
  'French Guiana': 'French Guianese',
  'French Polynesia': 'French Polynesian',
  'French Southern Territories': 'French',
  Gabon: 'Gabonese',
  Gambia: 'Gambian',
  Georgia: 'Georgian',
  Germany: 'German',
  Ghana: 'Ghanaian',
  Gibraltar: 'Gibraltarian',
  Greece: 'Greek',
  Greenland: 'Greenlandic',
  Grenada: 'Grenadian',
  Guadeloupe: 'Guadelou-pian',
  Guam: 'Guamanian',
  Guatemala: 'Guatemalan',
  Guernsey: 'Guernseyman',
  Guinea: 'Guinean',
  'Guinea-Bissau': 'Bissau-Guinean',
  Guyana: 'Guyanese',
  Haiti: 'Haitian',
  'Heard Island and McDonald Islands': 'Heard Islander',
  'Holy See': 'Vatican',
  Honduras: 'Honduran',
  'Hong Kong': 'Hong Konger',
  Hungary: 'Hungarian',
  Iceland: 'Icelandic',
  India: 'Indian',
  Indonesia: 'Indonesian',
  Iran: 'Iranian',
  Iraq: 'Iraqi',
  Ireland: 'Irish',
  'Isle of Man': 'Manx',
  Israel: 'Israeli',
  Italy: 'Italian',
  Jamaica: 'Jamaican',
  Japan: 'Japanese',
  Jersey: 'Jerseyman',
  Jordan: 'Jordanian',
  Kazakhstan: 'Kazakhstani',
  Kenya: 'Kenyan',
  Kiribati: 'I-Kiribati',
  Kuwait: 'Kuwaiti',
  Kyrgyzstan: 'Kyrgyzstani',
  'Lao People’s Democratic Republic': 'Laotian',
  Latvia: 'Latvian',
  Lebanon: 'Lebanese',
  Lesotho: 'Mosotho',
  Liberia: 'Liberian',
  Libya: 'Libyan',
  Liechtenstein: 'Liechtensteiner',
  Lithuania: 'Lithuanian',
  Luxembourg: 'Luxembourger',
  Macao: 'Macanese',
  Madagascar: 'Malagasy',
  Malawi: 'Malawian',
  Malaysia: 'Malaysian',
  Maldives: 'Maldivian',
  Mali: 'Malian',
  Malta: 'Maltese',
  'Marshall Islands': 'Marshallese',
  Martinique: 'Martinican',
  Mauritania: 'Mauritanian',
  Mauritius: 'Mauritian',
  Mayotte: 'Mahoran',
  Mexico: 'Mexican',
  Moldova: 'Moldovan',
  Monaco: 'Monégasque',
  Mongolia: 'Mongolian',
  Montenegro: 'Montenegrin',
  Montserrat: 'Montserratian',
  Morocco: 'Moroccan',
  Mozambique: 'Mozambican',
  Myanmar: 'Burmese',
  Namibia: 'Namibian',
  Nauru: 'Nauruan',
  Nepal: 'Nepalese',
  Netherlands: 'Dutch',
  'New Caledonia': 'New Caledonian',
  'New Zealand': 'New Zealander',
  Nicaragua: 'Nicaraguan',
  Niger: 'Nigerien',
  Nigeria: 'Nigerian',
  Niue: 'Niuean',
  'Norfolk Island': 'Norfolk Islander',
  'North Korea': 'North Korean',
  'North Macedonia': 'Macedonian',
  'Northern Mariana Islands': 'Northern Marianan',
  Norway: 'Norwegian',
  Oman: 'Omani',
  Pakistan: 'Pakistani',
  Palau: 'Palauan',
  Palestine: 'Palestinian',
  Panama: 'Panamanian',
  'Papua New Guinea': 'Papua New Guinean',
  Paraguay: 'Paraguayan',
  Peru: 'Peruvian',
  Philippines: 'Filipino',
  Pitcairn: 'Pitcairn Islander',
  Poland: 'Polish',
  Portugal: 'Portuguese',
  'Puerto Rico': 'Puerto Rican',
  Qatar: 'Qatari',
  Réunion: 'Réunionese',
  Romania: 'Romanian',
  Russia: 'Russian',
  Rwanda: 'Rwandan',
  'Saint Barthélemy': 'Barthélemois',
  'Saint Helena Ascension and Tristan da Cunha': 'Saint Helenian',
  'Saint Kitts and Nevis': 'Kittitian, Nevisian',
  'Saint Lucia': 'Saint Lucian',
  'Saint Martin': 'Saint-Martinois',
  'Saint Pierre and Miquelon': 'Saint-Pierrais',
  'Saint Vincent and the Grenadines': 'Saint Vincentian',
  Samoa: 'Samoan',
  'San Marino': 'Sammarinese',
  'São Tomé and Príncipe': 'São Toméan',
  'Saudi Arabia': 'Saudi Arabian',
  Senegal: 'Senegalese',
  Serbia: 'Serbian',
  Seychelles: 'Seychellois',
  'Sierra Leone': 'Sierra Leonean',
  Singapore: 'Singaporean',
  'Sint Maarten': 'Sint Maartenian',
  Slovakia: 'Slovak',
  Slovenia: 'Slovenian',
  'Solomon Islands': 'Solomon Islander',
  Somalia: 'Somali',
  'South Africa': 'South African',
  'South Georgia and the South Sandwich Islands': 'South Georgia Islander',
  'South Korea': 'South Korean',
  'South Sudan': 'South Sudanese',
  Spain: 'Spanish',
  'Sri Lanka': 'Sri Lankan',
  Sudan: 'Sudanese',
  Suriname: 'Surinamese',
  'Svalbard and Jan Mayen': 'Svalbardian',
  Sweden: 'Swedish',
  Switzerland: 'Swiss',
  Syria: 'Syrian',
  Taiwan: 'Taiwanese',
  Tajikistan: 'Tajikistani',
  Tanzania: 'Tanzanian',
  Thailand: 'Thai',
  'Timor-Leste': 'Timorese',
  Togo: 'Togolese',
  Tokelau: 'Tokelauan',
  Tonga: 'Tongan',
  'Trinidad and Tobago': 'Trinidadian, Tobagonian',
  Tunisia: 'Tunisian',
  Turkey: 'Turkish',
  Turkmenistan: 'Turkmen',
  'Turks and Caicos Islands': 'Turks and Caicos Islander',
  Tuvalu: 'Tuvaluan',
  Uganda: 'Ugandan',
  Ukraine: 'Ukrainian',
  'United Arab Emirates': 'Emirati',
  'United Kingdom': 'British',
  'United States': 'American',
  Uruguay: 'Uruguayan',
  Uzbekistan: 'Uzbekistani',
  Vanuatu: 'Ni‑Vanuatu',
  Venezuela: 'Venezuelan',
  Vietnam: 'Vietnamese',
  'Wallis and Futuna': 'Wallisian, Futunan',
  'Western Sahara': 'Sahrawi',
  Yemen: 'Yemeni',
  Zambia: 'Zambian',
  Zimbabwe: 'Zimbabwean',
};

export default Vue.extend({
  name: 'CreatePerspective',
  layout: 'project',
  data() {
    return {
      form: {
        dob: '',
        gender: '',
        nationality: '',
        text: '',
        category: 'subjective'
      },
      dobMenu: false,
      
      today: new Date().toISOString().substr(0, 10),
      minDOB: '1925-01-01',
      categories: [
        { text: this.$t('Cultural'), value: 'cultural' },
        { text: this.$t('Technic'), value: 'technic' },
        { text: this.$t('Subjective'), value: 'subjective' }
      ],
      isValid: false,
      dbError: "",
      genders: [
        { text: 'Male', value: 'M' },
        { text: 'Female', value: 'F' },
        { text: 'I prefer not to say', value: '?' }
      ],
      countries: [
        "Afghanistan","Albania","Algeria","American Samoa","Andorra","Angola",
        "Anguilla","Antarctica","Antigua and Barbuda","Argentina","Armenia","Aruba",
        "Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados",
        "Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia",
        "Bonaire Sint Eustatius and Saba","Bosnia and Herzegovina","Botswana",
        "Bouvet Island","Brazil","British Indian Ocean Territory","Brunei Darussalam",
        "Bulgaria","Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon","Canada",
        "Cayman Islands","Central African Republic","Chad","Chile","China","Christmas Island",
        "Cocos Keeling Islands","Colombia","Comoros","Congo",
        "Congo Democratic Republic of the","Cook Islands","Costa Rica","Côte d’Ivoire",
        "Croatia","Cuba","Curaçao","Cyprus","Czechia","Denmark","Djibouti","Dominica",
        "Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea",
        "Estonia","Eswatini","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland",
        "France","French Guiana","French Polynesia","French Southern Territories","Gabon",
        "Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada",
        "Guadeloupe","Guam","Guatemala","Guernsey","Guinea","Guinea-Bissau","Guyana","Haiti",
        "Heard Island and McDonald Islands","Holy See","Honduras","Hong Kong","Hungary",
        "Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy",
        "Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kiribati","Kuwait","Kyrgyzstan",
        "Lao People’s Democratic Republic","Latvia","Lebanon","Lesotho","Liberia","Libya",
        "Liechtenstein","Lithuania","Luxembourg","Macao","Madagascar","Malawi","Malaysia",
        "Maldives","Mali","Malta","Marshall Islands","Martinique","Mauritania","Mauritius",
        "Mayotte","Mexico","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco",
        "Mozambique","Myanmar","Namibia","Nauru","Nepal","Netherlands","New Caledonia",
        "New Zealand","Nicaragua","Niger","Nigeria","Niue","Norfolk Island","North Macedonia",
        "North Korea", "Northern Mariana Islands","Norway","Oman","Pakistan","Palau","Palestine","Panama",
        "Papua New Guinea","Paraguay","Peru","Philippines","Pitcairn","Poland","Portugal",
        "Puerto Rico","Qatar","Réunion","Romania","Russia","Rwanda","Saint Barthélemy",
        "Saint Helena Ascension and Tristan da Cunha","Saint Kitts and Nevis","Saint Lucia",
        "Saint Martin","Saint Pierre and Miquelon","Saint Vincent and the Grenadines","Samoa",
        "San Marino","São Tomé and Príncipe","Saudi Arabia","Senegal","Serbia","Seychelles",
        "Sierra Leone","Singapore","Sint Maarten","Slovakia","Slovenia","Solomon Islands",
        "Somalia","South Africa","South Georgia and the South Sandwich Islands", "South Korea",
        "South Sudan", "Spain","Sri Lanka","Sudan","Suriname","Svalbard and Jan Mayen","Sweden","Switzerland",
        "Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tokelau",
        "Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Turks and Caicos Islands",
        "Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States",
        "Uruguay","Uzbekistan","Vanuatu","Venezuela","Vietnam","Wallis and Futuna",
        "Western Sahara","Yemen","Zambia","Zimbabwe"
      ]
    }
  },
  computed: {
    ...mapGetters('auth', ['getUsername']),
    userRole(): string {
      return this.$store.state.auth.role || 'annotator'
    },
    sortedCountries(): string[] {
      return [...this.countries].sort((a, b) => a.localeCompare(b))
    }
  },
  methods: {
    async submitPerspective() {
      if (!(this.$refs.form as any).validate()) return
      const projectId = Number(this.$route.params.id)
      const userId = this.$store.state.auth.id
      const dob = new Date(this.form.dob)
      const diff = Date.now() - dob.getTime()
      const age = Math.floor(new Date(diff).getUTCFullYear() - 1970)
      const gender = this.form.gender || '?'

      const segments = [
        `Age: ${age}`,
        `Gender: ${gender}`
      ]
      if (this.form.nationality) {
        const dem = DEMONYMS[this.form.nationality] || this.form.nationality
        segments.push(`Nationality: ${dem}`)
      }
      const meta = segments.map(s => `${s},`).join(' ')
      const text = this.form.text.trim()
      const fullText = text ? `${meta} ${text}` : meta

      const payload: any = {
        text: fullText,
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

::v-deep .bold-label .v-label {
  font-weight: bold;
}
</style>