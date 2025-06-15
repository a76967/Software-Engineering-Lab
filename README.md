# Doccana – Extensão para a disciplina de Laboratório de Engenharia de Software

> Plataforma de anotação e análise de documentos, baseada no projeto open-source Doccano.

## Sumário

1. [Casos de Uso](#casos-de-uso)  
2. [Sobre a Doccana](#sobre-o-doccana)  
3. [Instalação e Quickstart](#instalação-e-quickstart)  
4. [Arquitetura do Projeto](#arquitetura-do-projeto)  
5. [Estrutura de Diretórios](#estrutura-de-diretórios)  
6. [Contribuição](#contribuição)  
7. [Licença e Citação](#licença-e-citação)  
8. [Contacto](#contacto)  

---

## Casos de Uso

---

### Tema 1: Gestão de Utilizadores  
- **Daniel** – Consultar Utilizador  
- **Gonçalo** – Criar Utilizador  
- **Juary** – Remover Utilizador  
- **Steve** – Editar Utilizador  

### Tema 2: Gestão de Desacordos entre Anotadores  
- **Daniel** – Filtragem e visualização baseada em perspetivas  
- **Gonçalo** – Associar anotações a perspetivas específicas  
- **Juary** – Geração de relatórios sobre as influências das perspetivas  
- **Steve** – Permitir que anotadores registem a sua perspetiva  

### Tema 3: Gestão de Perspetivas Anotadoras  
- **Daniel** – Apresentação lado a lado de anotações divergentes  
- **Gonçalo** – Sinalização visual de desacordos  
- **Juary** – Permitir discussão sobre as diferenças diretamente na interface  
- **Steve** – Registo e resolução de desacordos  

### Tema 4: Resolução Colaborativa de Desacordos  
*(Regras de Anotação e Votação)*  
- **Daniel** – Consultar votação final das regras de anotação  
- **Gonçalo** – Discutir regras de anotação em ambiente colaborativo  
- **Juary** – Votar nas regras de anotação  
- **Steve** – Definir regras de anotação e configurar votação  
- **Opcional**:  
  - Consultar histórico das discussões sobre regras de anotação  
  - Configurar notificações sobre novas votações  

### Tema 5: Relatórios de Desacordo e Perspetiva  
*(Reports)*  
- **Daniel** – Produzir estatísticas sobre anotações com vários filtros  
- **Gonçalo** – Produzir relatório sobre o histórico das anotações com vários filtros  
- **Juary** – Produzir relatório sobre anotadores com vários filtros  
- **Steve** – Produzir relatório sobre anotações com vários filtros  
- **Opcional**:  
  - Produzir estatísticas sobre o histórico das anotações com vários filtros  
  - Exportar relatório (PDF/CSV)  

---

## Sobre a Doccana

**Bem-vindo à Doccana**, a nossa solução moderna e intuitiva para anotação de documentos.  

- **Quem somos**  
  Somos Daniel Palma, Gonçalo Cordeiro, Juary Neto e Steve Rocha, alunos da unidade de Laboratório de Engenharia de Software (LES) na UAlg.  
- **Explicação do nome**  
  *Doccana* é o nosso toque pessoal no Doccano original: adicionámos um “a” em homenagem ao projeto-base, reforçando a nossa identidade.  
- **Porquê este projeto?**  
  Expandimos o Doccano com funcionalidades académicas e profissionais, mostrando a nossa capacidade de conceber UX e backend robustos.  
- **Professores**  
  Este trabalho foi proposto e orientado por Paula Ventura e Néstor Cataño.

---

## Instalação e Quickstart

### Pré-requisitos  
- Python 3.8+  
- Node.js 14+ e npm/yarn  
- Docker & Docker Compose (opcional)

### 1. Instalar com pip  
```bash
pip install doccana
doccana init
doccana createuser --username admin --password pass
doccana webserver --port 8000
# Em outro terminal:
doccana task
```
Acede em http://localhost:8000/.

### 2. Usar Docker  
```bash
docker pull doccano/doccano
docker run -d --name doccana \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_EMAIL=admin@example.com \
  -e ADMIN_PASSWORD=pass \
  -p 8000:8000 \
  doccano/doccano
```

### 3. Usar Docker Compose  
```bash
git clone https://github.com/doccano/doccano.git
cd doccano
cp docker/.env.example docker/.env
# Edita docker/.env conforme necessário
docker-compose -f docker/docker-compose.prod.yml up --build
```

### 4. (Opcional) Deploy em Cloud  
- **Heroku**: clique em *Deploy to Heroku* no repositório.  
- **AWS**: use o botão *Launch Stack* com o template CloudFormation.

---

## Arquitetura do Projeto

| Módulo              | Tecnologia                                            | Função                                     |
| ------------------- | ----------------------------------------------------- | ------------------------------------------ |
| Backend             | Python 3, Django, DRF, PostgreSQL/SQLite              | APIs REST, autenticação, lógica de negócio |
| Frontend            | Vue.js, Nuxt.js, Vuetify                              | UI responsiva, componentes de anotação     |
| Documentação (Docs) | Markdown + MkDocs + Material for MkDocs               | Guia de utilizador e desenvolvedor         |

---

## Estrutura de Diretórios

```txt
.
├── backend/             # Código Django REST  
├── frontend/            # App Nuxt/Vue.js + Vuetify  
├── docs/                # Documentação MkDocs  
├── tools/               # Scripts de packaging e CI  
├── README.md  
└── docker/              # Configuração Docker  
```

---

## Contribuição

1. Faz fork deste repositório.  
2. Cria uma branch: `git checkout -b feature/minha-ideia`.  
3. Implementa e testa as alterações.  
4. Faz commit: `git commit -m "Adiciona: minha-ideia"`.  
5. Push e abre um Pull Request.  

Consulta o [guia de contribuição oficial](https://github.com/doccano/doccano/wiki/How-to-Contribute-to-Doccano-Project).

---

## Licença e Citação

Este projeto estende o [Doccano](https://github.com/doccano/doccano) (MIT License).  
Por favor, cita-nos assim:

```tex
@misc{doccana,
  title={{doccana}: Plataforma de Anotação de Texto},
  author={Hiroki Nakayama and Takahiro Kubo and Junya Kamura and Yasufumi Taniguchi and Xu Liang},
  year={2018},
  url={https://github.com/doccano/doccano}
}
```

---

## Contacto

- Daniel Palma – a71177@ualg.pt  
- Gonçalo Cordeiro – a76967@ualg.pt  
- Juary Neto – a76931@ualg.pt  
- Steve Rocha – a76924@ualg.pt  

Obrigado por usar a **Doccana**!
