<template>
  <v-container
    fluid
    class="pa-4 d-flex flex-column"
    style="min-height:calc(100vh - 64px);"
  >
    <div class="mt-12"/>
    <h2 class="mt-4 mb-2">Annotations Report</h2>

    <v-card elevation="2" class="mb-6">
      <v-card-title>Report Filters</v-card-title>
      <v-divider/>
      <v-card-text>
        <v-form @submit.prevent="generateReport">
          <v-row dense>
            <v-col cols="12" sm="6" md="4">
              <v-select
                v-model="selectedVersions"
                :items="versionItems"
                item-text="text"
                item-value="id"
                label="Versions"
                multiple
                clearable
                dense
              />
            </v-col>
          </v-row>
          <v-row>
            <v-spacer/>
            <v-btn color="primary" type="submit">Generate Report</v-btn>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <v-card elevation="2" class="mb-6">
      <v-card-title>Preview</v-card-title>
      <v-divider/>

      <v-card-text>
        <v-alert v-if="errorMessage" dense type="error" class="mb-4">{{ errorMessage }}</v-alert>

        <div v-if="loading" class="text-center my-6">
          <v-progress-circular indeterminate color="primary"/>
        </div>

        <div v-else-if="reportData.length">
          <div v-for="section in reportData" :key="section.version" class="mb-4">
            <h3 class="mb-2">Version {{ section.versionNumber }}</h3>

            <v-simple-table dense class="annotation-preview mb-4">
              <thead class="primary">
                <tr>
                  <th class="white--text">Snippet</th>
                  <th v-for="lbl in labelKeys" :key="lbl" class="text-center white--text">
                    {{ lbl }}
                  </th>
                  <th class="text-center white--text">Abst.</th>
                  <th class="text-center white--text">X</th>
                  <th class="text-center white--text">Agree %</th>
                  <th class="text-center white--text">Auto</th>
                  <th class="text-center white--text">Manual</th>
                  <th class="text-center white--text">Top Label(s)</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="row in section.rows" :key="row.id">
                  <td>{{ row.snippet }}</td>
                  <td v-for="lbl in labelKeys" :key="lbl" class="text-center">
                    {{ row.labels[lbl] || 0 }}
                  </td>
                  <td class="text-center">{{ row.abstention || 0 }}</td>
                  <td class="text-center">{{ row.x || 0 }}</td>
                  <td class="text-center">{{ row.agreement }}%</td>
                  <td class="text-center">{{ row.autoState }}</td>
                  <td class="text-center">{{ row.manualState }}</td>
                  <td class="text-center">{{ row.winner }}</td>
                </tr>
              </tbody>
            </v-simple-table>
          </div>

          <div class="mb-6" style="color:#555">
            <strong>Description:</strong>
            This automatic report shows the label distribution across different dataset versions.
            The agreement percentage indicates the level of consistency among annotators.
          </div>
          <div v-if="reportData.length && projectInfo" class="mb-6" style="color:#555">
            <strong>General Info:</strong> {{ projectInfo }}
          </div>

          <div class="text-caption grey--text mb-6">
            Generated by {{ generatedBy }} on {{ generatedAt }}
          </div>
          <div class="text-caption grey--text mb-6">© Doccana - Software Engineering Lab</div>

          <v-btn class="mr-2" color="#B80000" dark @click="downloadPdf">Export to PDF</v-btn>
          <v-btn color="#1D6F42" dark @click="exportCsv">Export to CSV</v-btn>
        </div>

        <div v-else class="text-center grey--text my-6">
          No annotations. Adjust filters and click “Generate Report.”
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
// @ts-nocheck
import Vue from 'vue'
import autoTable from 'jspdf-autotable'
import {
  VContainer, VCard, VCardTitle, VDivider, VCardText, VForm,
  VRow, VCol, VSelect, VBtn, VSpacer, VProgressCircular,
  VAlert, VSimpleTable
} from 'vuetify/lib'
import ApiService from '~/services/api.service'

export default Vue.extend({
  name: 'ReportsAnnotationsGeneral',
  components: {
    VContainer, VCard, VCardTitle, VDivider, VCardText, VForm,
    VRow, VCol, VSelect, VBtn, VSpacer, VProgressCircular,
    VAlert, VSimpleTable
  },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data() {
    return {
      loading:false, reportData:[], selectedVersions:[], errorMessage:'',
      labelKeys:[], generatedBy:'', generatedAt:'', projectInfo:''
    }
  },
  computed:{
    versionItems() {
      const v=this.$store.getters['projects/projectVersions']||[]
      return v.map((x:any)=>({id:x.id,text:`Version ${x.versionNumber}`}))
    },
    projectId(): string {
      return this.$route.params.id
    }
  },
  async created(){
    const project=this.$store.getters['projects/project']||{}
    const name=project.name||''
    const versions=this.$store.getters['projects/projectVersions']||[]
    let memberNames:string[]=[]
    try{
      const members=await this.$repositories.member.list(this.projectId)
      memberNames=members.map((m:any)=>m.username)
    }catch(e){console.error(e)}
    let labelCount=0
    try{
      const [c,s,r]=await Promise.all([
        this.$services.categoryType.list(this.projectId),
        this.$services.spanType.list(this.projectId),
        this.$services.relationType.list(this.projectId)
      ])
      labelCount=c.length+s.length+r.length
    }catch(e){console.error(e)}
    this.projectInfo=`The project is named ${name}. It has ${versions.length} versions. The members of the project are ${memberNames.join(', ')}. The total number of labels are ${labelCount}.`
  },
  methods:{
    async generateReport(){
      this.loading=true
      const ids=this.selectedVersions.length?this.selectedVersions:this.versionItems.map(v=>v.id)
      const thr=parseInt(localStorage.getItem('disagreementThreshold')||'80',10)
      const all=new Set<string>(); const res:any=[]
      for(const id of ids){
        try{
          const {data}=await ApiService.get(`/projects/${id}/metrics/span-disagreements`)
          const decisions=JSON.parse(localStorage.getItem(`disagreementDecisions:${id}`)||'{}')
          const rows=(data||[]).map((r:any)=>{
            Object.keys(r.labels||{}).forEach(l=>all.add(l))
            const max=Math.max(...Object.values(r.labels||{}),0)
            const top=Object.entries(r.labels||{}).filter(([,c])=>c===max).map(([l])=>l).sort()
            const auto=r.agreement>=thr?'✓':r.agreement<thr/2?'✗':'⚠'
            let manual='—'
            if(decisions[r.id]!==undefined){
              const s=decisions[r.id]===true?'✗':decisions[r.id]===false?'✓':'⚠'
              if(s!==auto) manual=s
            }
            return{
              id:r.id,snippet:r.snippet,labels:r.labels||{},
              abstention:r.abstention||0,x:r.x||0,agreement:r.agreement,
              autoState:auto,manualState:manual,
              winner:top.length>1?`${top.join(', ')} (tied)`:top[0]||''
            }
          })
          const label=this.versionItems.find(v=>v.id===id)?.text||''
          res.push({version:id,versionNumber:label.replace('Version ',''),rows})
        }catch(e){console.error(e)}
      }
      this.labelKeys=Array.from(all).sort()
      this.reportData=res
      this.loading=false
      this.generatedBy=this.$store.getters['auth/getUsername']||'Unknown User'
      this.generatedAt=new Date().toLocaleString('pt-PT')
    },

    arrBufToB64(buf: ArrayBuffer) {
      const binary = Array.from(new Uint8Array(buf))
        .map(byte => String.fromCharCode(byte))
        .join('')
      return btoa(binary)
    },

    async downloadPdf () {
      const { jsPDF } = await import('jspdf')
      const JsPDFCtor = jsPDF || (await import('jspdf')).default
      const doc = new JsPDFCtor({ unit: 'pt', format: 'letter' })

      const fontUrl = require('~/static/DejaVuSans.ttf')
      if (!doc.getFontList().DejaVuSans) {
        const buf  = await (await fetch(fontUrl)).arrayBuffer()
        const u8   = new Uint8Array(buf)
        let binStr = ''
        const CHUNK = 0x8000
        for (let i = 0; i < u8.length; i += CHUNK) {
          binStr += String.fromCharCode(
            ...u8.subarray(i, i + CHUNK) as unknown as number[]
          )
        }
        doc.addFileToVFS('DejaVuSans.ttf', btoa(binStr))
        doc.addFont('DejaVuSans.ttf', 'DejaVuSans', 'normal', 'Identity-H')
        doc.addFont('DejaVuSans.ttf', 'DejaVuSans', 'bold', 'Identity-H')
      }
      doc.setFont('DejaVuSans', 'normal', 'Identity-H')

      const margin = 40
      let y = margin
      const pageWidth = doc.internal.pageSize.getWidth()
      const logoW = 110
      doc.addImage(require('~/static/doccana-logo.png'), 'PNG', (pageWidth - logoW) / 2, y, logoW, 40)
      y += 50

      doc.setFontSize(20).text('Annotations Report', margin, y)
      y += 30

      const head = [
        'Snippet', ...this.labelKeys, 'Abst.', 'X', 'Agree %',
        'Auto', 'Manual', 'Top Label'
      ]

      this.reportData.forEach(sec => {
        doc.setFont('DejaVuSans', 'bold').setFontSize(14).text(`Version ${sec.versionNumber}`, margin, y)
        y += 14

        const body = sec.rows.map((r:any, i:number) => [
          `${i + 1}. ${r.snippet}`,
          ...this.labelKeys.map(k => r.labels[k] || 0),
          r.abstention, r.x, `${r.agreement}%`,
          r.autoState, r.manualState, r.winner
        ])

        autoTable(doc, {
          head:[head],
          body,
          startY:y,
          styles:{ font:'DejaVuSans', fontSize:9, halign:'center' },
          columnStyles:{ 0:{ halign:'left' } },
          headStyles:{ fillColor:[99,118,171], textColor:255 },
          margin:{ left:margin, right:margin },
          theme:'striped'
        })
        // @ts-ignore
        y = doc.lastAutoTable.finalY + 20
      })

      doc.setFont('DejaVuSans', 'normal').setFontSize(11).setTextColor('#555')
      doc.text(
        'Description: This automatic report shows the label distribution across different dataset versions. The agreement percentage indicates the level of consistency among annotators.',
        margin, y, { maxWidth: doc.internal.pageSize.getWidth() - margin * 2 }
      )
      y += 36
      if(this.projectInfo){
        doc.text(this.projectInfo, margin, y, 
        { maxWidth: doc.internal.pageSize.getWidth() - margin * 2 })
        y += 36
      }

      doc.setFontSize(10).setTextColor('#333')
      doc.text(`Generated by ${this.generatedBy} on ${this.generatedAt}`, margin, y)
      y += 28
      doc.text('© Doccana - Software Engineering Lab', margin, y)

      doc.save('Annotations-Report.pdf')
    },

    exportCsv(){
      let csv=`Generated by,${this.generatedBy}\nGenerated at,${this.generatedAt}\n© Doccana - Software Engineering Lab\n\n`
      this.reportData.forEach(sec=>{
        csv+=`Version ${sec.versionNumber}\n`
        csv+=[
          'Snippet',...this.labelKeys,'Abstention','X','Agreement %',
          'Auto','Manual','Top Label'
        ].join(',')+'\n'
        sec.rows.forEach((r:any,i:number)=>{
          const cells=[`"${i+1}. ${r.snippet.replace(/"/g,'""')}"`,
            ...this.labelKeys.map(k=>r.labels[k]||0),
            r.abstention,r.x,`${r.agreement}%`,r.autoState,r.manualState,r.winner]
          csv+=cells.join(',')+'\n'
        })
        csv+='\n'
      })
      const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'})
      const a=document.createElement('a'); a.href=URL.createObjectURL(blob)
      a.download='annotations-report.csv'; document.body.appendChild(a); a.click(); a.remove()
    }
  }
})
</script>

<style scoped>
.annotation-preview{border-radius:4px}
.annotation-preview thead.primary{background:#6376ab!important}
.annotation-preview th.white--text{color:#fff!important}

.annotation-preview tbody tr:nth-child(odd){background:#f5f5f5}
.annotation-preview tbody tr:nth-child(even){background:#ffffff}
</style>