<template>
    <v-card>
      <v-alert v-if="dbError" type="error" dense>{{ dbError }}</v-alert>
      <v-card-text>
        <v-form ref="form" v-model="isValid" lazy-validation>
  
          <template v-if="adminPerspectives.length > 0">
            <v-text-field
              :value="adminPerspectives[0].name"
              label="Perspective"
              readonly
              class="bold-label"
            />
            <input type="hidden" v-model="selectedPerspective" />
          </template>

          <v-text-field
            v-model="form.name"
            label="Name"
            :rules="nameRules"
            :error="!!fieldErrors.name"
            :error-messages="fieldErrors.name"
            required
          />
          <v-textarea
            v-model="form.description"
            label="Description"
            rows="4"
            auto-grow
            :error="!!fieldErrors.description"
            :error-messages="fieldErrors.description"
          />

          <div v-for="field in extraItems" :key="field.id" class="mb-4">
            <v-text-field
              v-if="field.data_type==='string' || field.data_type==='number'"
              v-model="form.extra[field.name]"
              :type="field.data_type === 'number' ? 'number' : 'text'"
              :label="`${field.name}${field.required ? ' *' : ''}`"
              :rules="field.required ? extraRules(field) : []"
              :required="field.required"
            />
            <v-select
              v-else-if="field.data_type==='boolean'"
              v-model="form.extra[field.name]"
              :items="booleanOptions"
              :label="`${field.name}${field.required ? ' *' : ''}`"
              :rules="field.required ? extraRules(field) : []"
              item-text="text"
              item-value="value"
            />
          </div>
          
          <v-alert
            v-if="autoEnumValues"
            type="info"
            dense
            class="mb-2"
          >
            Auto‐filled options: {{ autoEnumValues.join(', ') }}
          </v-alert>
          <v-alert
            v-else-if="newItem.name==='Age'"
            type="info"
            dense
            class="mb-2"
          >
            Age must be between 0 and 100.
          </v-alert>
          <v-alert
            v-else-if="newItem.name==='Weight'"
            type="info"
            dense
            class="mb-2"
          >
            Weight values are in kg.
          </v-alert>
          <v-alert
            v-else-if="newItem.name==='Height'"
            type="info"
            dense
            class="mb-2"
          >
            Height values are in cm.
          </v-alert>

        </v-form>

        <v-divider class="my-4" />
        <h6 class="mb-2">Items</h6>
        <v-simple-table v-if="itemsToAdd.length" dense>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(it,i) in itemsToAdd" :key="i">
              <td>{{ it.name }}</td>
              <td>{{ it.data_type }}</td>
              <td>
                <v-btn icon small @click="itemsToAdd.splice(i,1)">
                  <v-icon small>mdi-delete</v-icon>
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-simple-table>

        <v-form ref="itemForm" v-model="itemValid" lazy-validation>
          <v-row align="center" class="mt-2">
            <v-col cols="4">
              <v-text-field
                v-model="newItem.name"
                label="Item Name"
                :rules="itemNameRules"
                dense
              />
            </v-col>
            <v-col cols="3">
              <v-select
                v-model="newItem.data_type"
                :items="types"
                label="Data Type"
                :rules="itemTypeRules"
                :disabled="isTypeLocked"
                dense
              />
            </v-col>

            <!-- manual‐only enum input (hide for auto cases) -->
            <template v-if="newItem.data_type==='enum' && !autoEnumValues">
              <v-col cols="7">
                <v-text-field
                  v-model="newItem.enumValues"
                  label="Enum Values (comma‐separated)"
                  dense
                  :rules="[v => !!v || 'Enum values required']"
                />
              </v-col>
            </template>

            <v-col cols="2">
              <v-btn
                :disabled="!itemValid"
                color="primary"
                @click="addItem"
              >Add</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-end">
        <v-btn text @click="goBack">Cancel</v-btn>
        <v-btn
          color="primary"
          @click="submit"
          :disabled="!isValid"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import axios from 'axios'
  
  export default Vue.extend({
    layout: 'project',
    middleware: ['check-auth','auth','setCurrentProject','isProjectAdmin'],
    data() {
      return {
        form: { name: '', description: '', extra: {} as Record<string, any> },
        isValid: false,
        dbError: '',
        nameRules: [(v: string) => !!v || 'Name is required'],

        types: ['string','number','boolean','enum'],
        newItem: { name: '', data_type: '', enumValues: '' },
        // note: use `enum_values` to match backend field name
        itemsToAdd: [] as Array<{name:string,data_type:string,enum_values?:string[]}>,
        itemNameRules: [(v: string) => !!v || 'Item name required'],
        itemTypeRules: [(v: string) => !!v || 'Type required'],
        itemValid: false,

        adminPerspectives: [] as any[],
        selectedPerspective: null as number|null,
        extraItems: [] as any[],

        booleanOptions: [
          { text: 'Yes', value: true },
          { text: 'No',  value: false }
        ],

        countries: ["Åland Islands",
          "Albania",
          "Algeria",
          "American Samoa",
          "Andorra",
          "Angola",
          "Anguilla",
          "Antarctica",
          "Antigua and Barbuda",
          "Argentina",
          "Armenia",
          "Aruba",
          "Australia",
          "Austria",
          "Azerbaijan",
          "Bahamas",
          "Bahrain",
          "Bangladesh",
          "Barbados",
          "Belarus",
          "Belgium",
          "Belize",
          "Benin",
          "Bermuda",
          "Bhutan",
          "Bolivia",
          "Bonaire, Sint Eustatius and Saba",
          "Bosnia and Herzegovina",
          "Botswana",
          "Bouvet Island",
          "Brazil",
          "British Indian Ocean Territory",
          "Brunei Darussalam",
          "Bulgaria",
          "Burkina Faso",
          "Burundi",
          "Cabo Verde",
          "Cambodia",
          "Cameroon",
          "Canada",
          "Cayman Islands",
          "Central African Republic",
          "Chad",
          "Chile",
          "China",
          "Christmas Island",
          "Cocos Islands",
          "Colombia",
          "Comoros",
          "Congo Republic",
          "DRCongo",
          "Cook Islands",
          "Costa Rica",
          "Croatia",
          "Cuba",
          "Curaçao",
          "Cyprus",
          "Czechia",
          "Denmark",
          "Djibouti",
          "Dominica",
          "Dominican Republic",
          "Ecuador",
          "Egypt",
          "El Salvador",
          "England",
          "Equatorial Guinea",
          "Eritrea",
          "Estonia",
          "Eswatini",
          "Ethiopia",
          "Falkland Islands",
          "Faroe Islands",
          "Fiji",
          "Finland",
          "France",
          "French Guiana",
          "French Polynesia",
          "French Southern Territories",
          "Gabon",
          "Gambia",
          "Georgia",
          "Germany",
          "Ghana",
          "Gibraltar",
          "Greece",
          "Greenland",
          "Grenada",
          "Guadeloupe",
          "Guam",
          "Guernsey",
          "Guinea",
          "Guinea-Bissau",
          "Guyana",
          "Haiti",
          "Heard Island and McDonald Islands",
          "Holy See",
          "Honduras",
          "Hong Kong",
          "Hungary",
          "Iceland",
          "India",
          "Indonesia",
          "Iran",
          "Iraq",
          "Ireland",
          "Isle of Man",
          "Israel",
          "Italy",
          "Jamaica",
          "Japan",
          "Jersey",
          "Jordan",
          "Kazakhstan",
          "Kenya",
          "Kiribati",
          "North Korea",
          "Kosovo",
          "Kuwait",
          "Kyrgyzstan",
          "Lao People's Democratic Republic",
          "Latvia",
          "Lebanon",
          "Lesotho",
          "Liberia",
          "Libya",
          "Liechtenstein",
          "Lithuania",
          "Luxembourg",
          "Macao",
          "Madagascar",
          "Malawi",
          "Malaysia",
          "Maldives",
          "Mali",
          "Malta",
          "Marshall Islands",
          "Martinique",
          "Mauritania",
          "Mauritius",
          "Mayotte",
          "Mexico",
          "Micronesia",
          "Moldova",
          "Monaco",
          "Mongolia",
          "Montenegro",
          "Montserrat",
          "Morocco",
          "Mozambique",
          "Myanmar",
          "Namibia",
          "Nauru",
          "Nepal",
          "Netherlands",
          "New Caledonia",
          "New Zealand",
          "Nicaragua",
          "Niger",
          "Nigeria",
          "Niue",
          "Norfolk Island",
          "North Korea",
          "North Macedonia",
          "Northern Ireland",
          "Northern Mariana Islands",
          "Norway",
          "Oman",
          "Pakistan",
          "Palau",
          "Panama",
          "Papua New Guinea",
          "Paraguay",
          "Peru",
          "Philippines",
          "Pitcairn",
          "Poland",
          "Portugal",
          "Puerto Rico",
          "Qatar",
          "Réunion",
          "Romania",
          "Russian Federation",
          "Rwanda",
          "Saint Barthélemy",
          "Saint Helena, Ascension and Tristan da Cunha",
          "Saint Kitts and Nevis",
          "Saint Lucia",
          "Saint Martin",
          "Saint Pierre and Miquelon",
          "Saint Vincent and the Grenadines",
          "Samoa",
          "San Marino",
          "Sao Tome and Principe",
          "Saudi Arabia",
          "Scotland",
          "Senegal",
          "Serbia",
          "Seychelles",
          "Sierra Leone",
          "Singapore",
          "Sint Maarten",
          "Slovakia",
          "Slovenia",
          "Solomon Islands",
          "Somalia",
          "South Africa",
          "South Korea",
          "South Georgia and the South Sandwich Islands",
          "South Sudan",
          "Spain",
          "Sri Lanka",
          "Sudan",
          "Suriname",
          "Svalbard and Jan Mayen",
          "Sweden",
          "Switzerland",
          "Syrian Arab Republic",
          "Taiwan, Province of China",
          "Tajikistan",
          "Tanzania, United Republic of",
          "Thailand",
          "Timor-Leste",
          "Togo",
          "Tokelau",
          "Tonga",
          "Trinidad and Tobago",
          "Tunisia",
          "Turkey",
          "Turkmenistan",
          "Tuvalu",
          "Uganda",
          "Ukraine",
          "United Arab Emirates",
          "United States of America",
          "Uruguay",
          "Uzbekistan",
          "Vanuatu",
          "Venezuela",
          "Vietnam",
          "Wales",
          "Western Sahara",
          "Yemen",
          "Zambia",
          "Zimbabwe"
      ],
      fieldErrors: {} as Record<string,string[]>
      }
    },
    computed: {
      projectId(): number { return Number(this.$route.params.id) },
      userId(): number     { return this.$store.state.auth.id },
      autoEnumValues(): string[]|null {
        const name = this.newItem.name
        if (name === 'Gender')       return ['M','F']
        if (name === 'Continent')    return ['Africa','Antarctica','Asia','Europe','North America','Oceania','South America']
        if (name === 'Country')     return this.countries
        return null
      },
      isTypeLocked(): boolean {
        const n = this.newItem.name
        if (['Gender','Continent','Country','Age','Weight','Height'].includes(n)) return true
        return false
      }
    },
    watch: {
      'newItem.name': {
        immediate: true,
        handler(val: string) {
          const auto = this.autoEnumValues
          if (auto) {
            this.newItem.data_type = 'enum'
            this.newItem.enumValues = auto.join(', ')
          }
          else if (['Age','Weight','Height'].includes(val)) {
            this.newItem.data_type = 'number'
            this.newItem.enumValues = ''
          }
          else if (this.newItem.data_type === 'enum') {
            this.newItem.enumValues = ''
          }
        }
      }
    },
    async mounted() {
      await this.checkExisting()
      await this.fetchAdminPerspectives()
      if (this.adminPerspectives.length) {
        this.selectedPerspective = this.adminPerspectives[0].id
        await this.fetchExtraItems()
      }
    },
    methods: {
      async checkExisting() {
        try {
          const res = await axios.get(`/v1/projects/${this.projectId}/admin-perspectives/`)
          const exists = (res.data.results || res.data).length > 0
          if (exists) {
            this.$router.push(this.localePath(`/projects/${this.projectId}/admin-perspectives`))
          }
        } catch (e) {}
      },

      async fetchAdminPerspectives () {
        try {
          this.adminPerspectives = await this.$repositories.adminPerspective.list(
            Number(this.$route.params.id)
          )
        } catch {
          this.adminPerspectives = []
        }
      },

      async fetchExtraItems () {
        if (!this.selectedPerspective) return
        try {
          const res = await this.$repositories.perspectiveField.list(
            Number(this.$route.params.id),
            this.selectedPerspective
          )
          this.extraItems = res
        } catch {
          this.extraItems = []
        }
        if (!this.extraItems.length) {
          this.dbError = 'No fields defined by project admin.'
        }
      },

      addItem() {
        if (!(this.$refs.itemForm as any).validate()) return

        const item: any = {
          name: this.newItem.name,
          data_type: this.newItem.data_type
        }
        if (this.newItem.data_type === 'enum') {
          // build enum_values array instead of `enum`
          item.enum_values = this.autoEnumValues
            ? this.autoEnumValues
            : this.newItem.enumValues
                .split(',')
                .map(s => s.trim())
                .filter(Boolean)
        }
        this.itemsToAdd.push(item)

        // reset form
        this.newItem.name = ''
        this.newItem.data_type = ''
        this.newItem.enumValues = ''
        ;(this.$refs.itemForm as any).resetValidation()
      },

      async submit() {
        // clear previous field errors
        this.fieldErrors = {}
        if (!(this.$refs.form as any).validate()) return
        // 1) Create the AdminPerspective
        let createdId: number
        try {
          const { data } = await axios.post(
            `/v1/projects/${this.projectId}/admin-perspectives/`,
            {
              name: this.form.name,
              description: this.form.description,
              user: this.userId
            }
          )
          createdId = data.id
        } catch (err: any) {
          console.error('AdminPerspective create error:', err.response?.data)
          const errs = err.response?.data || {}
          // assign field errors if present
          const keys = ['name','description']
          keys.forEach(k => {
            if (Array.isArray(errs[k])) this.fieldErrors[k] = errs[k]
          })
          // generic error message
          this.dbError = errs.detail 
            ? String(errs.detail)
            : 'Failed to create perspective.'
          return
        }

        // 2) Create each PerspectiveItem
        for (const it of this.itemsToAdd) {
          const payload: any = {
            name: it.name,
            data_type: it.data_type,
            admin_perspective: createdId
          }
          // if enum, backend expects `enum_values`
          if (it.data_type === 'enum' && it.enum_values) {
            payload.enum_values = it.enum_values
          }
          try {
            await axios.post(
              `/v1/projects/${this.projectId}/perspective-items/`,
              payload
            )
          } catch (err: any) {
            console.error('PerspectiveItem create error:', err.response?.data)
            this.dbError = JSON.stringify(err.response?.data || { detail: 'Item creation failed' })
            return
          }
        }

        // 3) Navigate on success
        this.$router.push({
          path: this.localePath('/message'),
          query: {
            message: 'Admin perspective created successfully!',
            redirect: this.localePath(`/projects/${this.projectId}/admin-perspectives`)
          }
        })
      },
      goBack() {
        this.$router.push(this.localePath(`/projects/${this.projectId}/admin-perspectives`))
      }
    }
  })
  </script>
  
  <style scoped>
  .v-card { max-width: 600px; margin: 20px auto; padding: 20px; }
  </style>