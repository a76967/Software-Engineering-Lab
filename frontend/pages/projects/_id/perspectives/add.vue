<template>
  <v-card>
    <v-alert v-if="dbError" type="error" dense>
      {{ dbError }}
    </v-alert>

    <v-card-text>
      <v-form ref="form" v-model="isValid" lazy-validation>
        <v-select
          v-model="form.category"
          :items="categories"
          label="Category"
          required
          class="bold-label"
        />

        <v-textarea
          v-model="form.text"
          class="custom-input"
          :label="$t('Text')"
          counter="2000"
          rows="10"
          auto-grow
          required
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
// @ts-nocheck
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
  'England': 'English',
  'Scotland': 'Scottish',
  'Wales': 'Welsh',
  'Northern Ireland': 'Northern Irish',
};

const COUNTRY_TO_CONTINENT: Record<string, string> = {
  "Afghanistan": "Asia",
  "Albania": "Europe",
  "Algeria": "Africa",
  "American Samoa": "Oceania",
  "Andorra": "Europe",
  "Angola": "Africa",
  "Anguilla": "North America",
  "Antarctica": "Antarctica",
  "Antigua and Barbuda": "North America",
  "Argentina": "South America",
  "Armenia": "Asia",
  "Aruba": "North America",
  "Australia": "Oceania",
  "Austria": "Europe",
  "Azerbaijan": "Asia",
  "Bahamas": "North America",
  "Bahrain": "Asia",
  "Bangladesh": "Asia",
  "Barbados": "North America",
  "Belarus": "Europe",
  "Belgium": "Europe",
  "Belize": "North America",
  "Benin": "Africa",
  "Bermuda": "North America",
  "Bhutan": "Asia",
  "Bolivia": "South America",
  "Bosnia and Herzegovina": "Europe",
  "Botswana": "Africa",
  "Bouvet Island": "Antarctica",
  "Brazil": "South America",
  "British Indian Ocean Territory": "Asia",
  "Brunei Darussalam": "Asia",
  "Bulgaria": "Europe",
  "Burkina Faso": "Africa",
  "Burundi": "Africa",
  "Cabo Verde": "Africa",
  "Cambodia": "Asia",
  "Cameroon": "Africa",
  "Canada": "North America",
  "Cayman Islands": "North America",
  "Central African Republic": "Africa",
  "Chad": "Africa",
  "Chile": "South America",
  "China": "Asia",
  "Christmas Island": "Asia",
  "Cocos Keeling Islands": "Asia",
  "Colombia": "South America",
  "Comoros": "Africa",
  "Congo": "Africa",
  "Congo Democratic Republic of the": "Africa",
  "Cook Islands": "Oceania",
  "Costa Rica": "North America",
  "Côte d’Ivoire": "Africa",
  "Croatia": "Europe",
  "Cuba": "North America",
  "Curaçao": "North America",
  "Cyprus": "Asia",
  "Czechia": "Europe",
  "Denmark": "Europe",
  "Djibouti": "Africa",
  "Dominica": "North America",
  "Dominican Republic": "North America",
  "Ecuador": "South America",
  "Egypt": "Africa",
  "El Salvador": "North America",
  "Equatorial Guinea": "Africa",
  "Eritrea": "Africa",
  "Estonia": "Europe",
  "Eswatini": "Africa",
  "Ethiopia": "Africa",
  "Falkland Islands": "South America",
  "Faroe Islands": "Europe",
  "Fiji": "Oceania",
  "Finland": "Europe",
  "France": "Europe",
  "French Guiana": "South America",
  "French Polynesia": "Oceania",
  "French Southern Territories": "Antarctica",
  "Gabon": "Africa",
  "Gambia": "Africa",
  "Georgia": "Asia",
  "Germany": "Europe",
  "Ghana": "Africa",
  "Gibraltar": "Europe",
  "Greece": "Europe",
  "Greenland": "North America",
  "Grenada": "North America",
  "Guadeloupe": "North America",
  "Guam": "Oceania",
  "Guatemala": "North America",
  "Guernsey": "Europe",
  "Guinea": "Africa",
  "Guinea-Bissau": "Africa",
  "Guyana": "South America",
  "Haiti": "North America",
  "Heard Island and McDonald Islands": "Antarctica",
  "Holy See": "Europe",
  "Honduras": "North America",
  "Hong Kong": "Asia",
  "Hungary": "Europe",
  "Iceland": "Europe",
  "India": "Asia",
  "Indonesia": "Asia",
  "Iran": "Asia",
  "Iraq": "Asia",
  "Ireland": "Europe",
  "Isle of Man": "Europe",
  "Israel": "Asia",
  "Italy": "Europe",
  "Jamaica": "North America",
  "Japan": "Asia",
  "Jersey": "Europe",
  "Jordan": "Asia",
  "Kazakhstan": "Asia",
  "Kenya": "Africa",
  "Kiribati": "Oceania",
  "Kuwait": "Asia",
  "Kyrgyzstan": "Asia",
  "Lao People’s Democratic Republic": "Asia",
  "Latvia": "Europe",
  "Lebanon": "Asia",
  "Lesotho": "Africa",
  "Liberia": "Africa",
  "Libya": "Africa",
  "Liechtenstein": "Europe",
  "Lithuania": "Europe",
  "Luxembourg": "Europe",
  "Macao": "Asia",
  "Madagascar": "Africa",
  "Malawi": "Africa",
  "Malaysia": "Asia",
  "Maldives": "Asia",
  "Mali": "Africa",
  "Malta": "Europe",
  "Marshall Islands": "Oceania",
  "Martinique": "North America",
  "Mauritania": "Africa",
  "Mauritius": "Africa",
  "Mayotte": "Africa",
  "Mexico": "North America",
  "Moldova": "Europe",
  "Monaco": "Europe",
  "Mongolia": "Asia",
  "Montenegro": "Europe",
  "Montserrat": "North America",
  "Morocco": "Africa",
  "Mozambique": "Africa",
  "Myanmar": "Asia",
  "Namibia": "Africa",
  "Nauru": "Oceania",
  "Nepal": "Asia",
  "Netherlands": "Europe",
  "New Caledonia": "Oceania",
  "New Zealand": "Oceania",
  "Nicaragua": "North America",
  "Niger": "Africa",
  "Nigeria": "Africa",
  "Niue": "Oceania",
  "Norfolk Island": "Oceania",
  "North Korea": "Asia",
  "North Macedonia": "Europe",
  "Northern Mariana Islands": "Oceania",
  "Norway": "Europe",
  "Oman": "Asia",
  "Pakistan": "Asia",
  "Palau": "Oceania",
  "Palestine": "Asia",
  "Panama": "North America",
  "Papua New Guinea": "Oceania",
  "Paraguay": "South America",
  "Peru": "South America",
  "Philippines": "Asia",
  "Pitcairn": "Oceania",
  "Poland": "Europe",
  "Portugal": "Europe",
  "Puerto Rico": "North America",
  "Qatar": "Asia",
  "Réunion": "Africa",
  "Romania": "Europe",
  "Russia": "Europe",
  "Rwanda": "Africa",
  "Saint Barthélemy": "North America",
  "Saint Helena Ascension and Tristan da Cunha": "Africa",
  "Saint Kitts and Nevis": "North America",
  "Saint Lucia": "North America",
  "Saint Martin": "North America",
  "Saint Pierre and Miquelon": "North America",
  "Saint Vincent and the Grenadines": "North America",
  "Samoa": "Oceania",
  "San Marino": "Europe",
  "São Tomé and Príncipe": "Africa",
  "Saudi Arabia": "Asia",
  "Senegal": "Africa",
  "Serbia": "Europe",
  "Seychelles": "Africa",
  "Sierra Leone": "Africa",
  "Singapore": "Asia",
  "Sint Maarten": "North America",
  "Slovakia": "Europe",
  "Slovenia": "Europe",
  "Solomon Islands": "Oceania",
  "Somalia": "Africa",
  "South Africa": "Africa",
  "South Georgia and the South Sandwich Islands": "Antarctica",
  "South Korea": "Asia",
  "South Sudan": "Africa",
  "Spain": "Europe",
  "Sri Lanka": "Asia",
  "Sudan": "Africa",
  "Suriname": "South America",
  "Svalbard and Jan Mayen": "Europe",
  "Sweden": "Europe",
  "Switzerland": "Europe",
  "Syria": "Asia",
  "Taiwan": "Asia",
  "Tajikistan": "Asia",
  "Tanzania": "Africa",
  "Thailand": "Asia",
  "Timor-Leste": "Asia",
  "Togo": "Africa",
  "Tokelau": "Oceania",
  "Tonga": "Oceania",
  "Trinidad and Tobago": "North America",
  "Tunisia": "Africa",
  "Turkey": "Asia",
  "Turkmenistan": "Asia",
  "Turks and Caicos Islands": "North America",
  "Tuvalu": "Oceania",
  "Uganda": "Africa",
  "Ukraine": "Europe",
  "United Arab Emirates": "Asia",
  "United Kingdom": "Europe",
  "United States": "North America",
  "Uruguay": "South America",
  "Uzbekistan": "Asia",
  "Vanuatu": "Oceania",
  "Venezuela": "South America",
  "Vietnam": "Asia",
  "Wallis and Futuna": "Oceania",
  "Western Sahara": "Africa",
  "Yemen": "Asia",
  "Zambia": "Africa",
  "Zimbabwe": "Africa",
  'England': 'Europe',
  'Scotland': 'Europe',
  'Wales': 'Europe',
  'Northern Ireland': 'Europe',
};

export default Vue.extend({
  name: 'CreatePerspective',
  layout: 'project',

  data () {
    return {
      form: {
        text: '',
        category: 'subjective'
      },
      categories: [
        { text: this.$t('Cultural'),   value: 'cultural'  },
        { text: this.$t('Technic'),    value: 'technic'   },
        { text: this.$t('Subjective'), value: 'subjective'}
      ],
      isValid: false,
      dbError: ''
    }
  },

  computed: {
    ...mapGetters('auth', ['getUsername']),
    userRole (): string {
      return this.$store.state.auth.role || 'annotator'
    }
  },

  async mounted () {
    await this.checkExistingPerspective()
  },

  methods: {
    parseBirthday (txt: string) {
      const m = txt.match(/\b(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b/)
      if (!m) return undefined
      let d   = parseInt(m[1], 10)
      let mth = parseInt(m[2], 10)
      let y   = parseInt(m[3], 10)
      if (y < 100) y += y >= 30 ? 1900 : 2000
      if (d > 12 && mth <= 12) {
        [d, mth] = [mth, d]
      }
      const date = new Date(y, mth - 1, d)
      return isNaN(date.getTime()) ? undefined : date
    },

    calcAge (born: Date) {
      const today = new Date()
      let age = today.getFullYear() - born.getFullYear()
      const m = today.getMonth() - born.getMonth()
      if (m < 0 || (m === 0 && today.getDate() < born.getDate())) age--
      return age
    },

    extractInfo (text: string) {
      const lower = text.toLowerCase()
      let age, gender, country, generation;
      let nationality = 'Unknown';

      let m = lower.match(/(?:age|idade)[:\s]*([0-9]{1,3})/)
      if (!m) m = lower.match(/(\d{1,3})\s*(?:years? old|anos?)/)
      if (!m) m = lower.match(/(?:i am|i'm|im|eu tenho|tenho)\s+(\d{1,3})/)
      if (m) {
        age = parseInt(m[1], 10)
      }

      if (age === undefined) {
        const bday = this.parseBirthday(lower)
        if (bday) age = this.calcAge(bday)
      }

      if (age !== undefined && (age < 0 || age > 100)) {
        age = undefined
      }

      const gMatch = lower.match(/\b(male|female|man|woman|masculino|feminino|homem|mulher|guy|girl|boy|he|she|him|her)\b/)
      if (gMatch) {
        gender = /(female|feminino|woman|mulher|girl|she|her)/.test(gMatch[1]) ? 'F' : 'M'
      }

      for (const [c, dem] of Object.entries(DEMONYMS)) {
        if (lower.includes(c.toLowerCase()) || lower.includes(dem.toLowerCase())) {
          country = c; nationality = dem
          break
        }
      }
      const continent = country ? COUNTRY_TO_CONTINENT[country] : 'Unknown'

      if (age !== undefined) {
        if (age <= 26) generation = 'Gen Z'
        else if (age <= 42) generation = 'Millennial'
        else if (age <= 58) generation = 'Gen X'
        else if (age <= 77) generation = 'Baby Boomer'
        else generation = 'Silent'
      }

      return { age, gender, nationality, generation, continent }
    },

    async checkExistingPerspective () {
      const projectId = this.$route.params.id
      const userId    = this.$store.state.auth.id
      try {
        const list = await this.$repositories.perspective.list(projectId)
        const existing = list.find((p:any) => p.userId === userId)
        if (existing) {
          this.$router.push(
            this.localePath(`/projects/${projectId}/perspectives/edit?perspectiveId=${existing.id}`)
          )
        }
      } catch (e) {
        console.error('Failed to check existing ', e)
      }
    },

    async submitPerspective () {
      const projectId = Number(this.$route.params.id)
      const userId    = this.$store.state.auth.id
      const rawText   = this.form.text.trim()
      const info      = this.extractInfo(rawText)

      if (info.age === undefined || info.gender === undefined) {
        this.dbError = 'Age and gender must be specified (number or birthday).'
        return
      }

      const segs = [
        `Age: ${info.age}`,
        `Gender: ${info.gender}`,
        `Nationality: ${info.nationality}`,
        `Continent: ${info.continent}`
      ]
      if (info.generation) segs.push(`Generation: ${info.generation}`)

      const full = rawText ? `${segs.join(', ')}. ${rawText}` : segs.join(', ')
      const payload = {
        text: full,
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
      } catch (err:any) {
        console.error(err)
        this.dbError = "Can't access our database!"
      }
    },

    goBack () {
      this.$router.push(
        this.localePath(`/projects/${this.$route.params.id}/perspectives`)
      )
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