window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      formDialog: {
        show: false,
        data: {}
      },
      unitTypes: [
        {value: 'token', label: 'per 1000 Tokens'},
        {value: 'request', label: 'per Request'}
      ],
      agents: [],
      apiKeys: [],
      agentsTable: {
        columns: [
          {name: 'name', align: 'left', label: 'Name', field: 'name'},
          {name: 'id', align: 'left', label: 'ID', field: 'id'},
          {name: 'api_url', align: 'left', label: 'URL', field: 'api_url'},
          {
            name: 'api_key',
            align: 'left',
            label: 'Key',
            field: row => row.api_key ?? 'N/A'
          },
          {
            name: 'wallet_id',
            align: 'left',
            label: 'Wallet',
            field: 'wallet_id'
          },
          {name: 'cost', align: 'left', label: 'Cost', field: 'price_per_unit'}
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      apiKeysTable: {
        columns: [
          {
            name: 'agent',
            align: 'left',
            label: 'Agent',
            field: 'agent_id',
            format: id => {
              const agent = this.agents.find(l => l.id == id)
              return agent ? agent.name : 'N/A'
            }
          },
          {name: 'active', align: 'left', label: 'Active', field: 'active'},
          {name: 'id', align: 'left', label: 'ID', field: 'id'},
          {
            name: 'created_at',
            align: 'left',
            label: 'Created At',
            field: 'created_at',
            format: date => {
              return new Date(date).toLocaleString()
            }
          }
        ],
        pagination: {
          rowsPerPage: 10
        }
      }
    }
  },

  methods: {
    getAgents() {
      LNbits.api
        .request(
          'GET',
          '/proxyllm/api/v1/agents?all_wallets=true',
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          this.agents = response.data
          console.log(this.agents)
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    getApiKeys() {
      LNbits.api
        .request(
          'GET',
          '/proxyllm/api/v1/accesskeys?all_wallets=true',
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          console.log(response.data)
          this.apiKeys = response.data
          console.log(this.apiKeys)
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    resetFormDialog() {
      this.formDialog.show = false
      this.formDialog.data = {}
    },
    openUpdateForm(id) {
      const agent = this.agents.find(l => l.id === id)
      this.formDialog.data = {...agent}
      this.formDialog.show = true
    },
    deleteAgent(id) {
      LNbits.utils
        .confirmDialog('Are you sure you want to delete this agent?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              `/proxyllm/api/v1/agents/${id}`,
              this.g.user.wallets[0].adminkey
            )
            .then(() => {
              this.agents = this.agents.filter(l => l.id !== id)
              this.$q.notify({
                message: `Agent deleted.`,
                timeout: 700
              })
            })
            .catch(error => {
              LNbits.utils.notifyApiError(error)
            })
        })
    },
    sendForm() {
      const wallet = this.g.user.wallets.find(
        w => w.id === this.formDialog.data.wallet_id
      )
      const data = {...this.formDialog.data}
      if (!data.cost) data.cost = 0
      if (data.id) {
        this.updateAgent(wallet, data)
      } else {
        this.createAgent(wallet, data)
      }
    },
    createAgent(wallet, data) {
      LNbits.api
        .request('POST', '/proxyllm/api/v1/agents', wallet.adminkey, data)
        .then(response => {
          this.agents.push(response.data)
          this.$q.notify({
            type: 'positive',
            message: `Agent created.`,
            timeout: 700
          })
          this.resetFormDialog()
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    updateAgent(wallet, data) {
      LNbits.api
        .request(
          'PUT',
          `/proxyllm/api/v1/agents/${data.id}`,
          wallet.adminkey,
          data
        )
        .then(response => {
          const index = this.agents.findIndex(l => l.id === data.id)
          this.agents.splice(index, 1, response.data)
          this.$q.notify({
            type: 'positive',
            message: `Agent updated.`,
            timeout: 700
          })
          this.resetFormDialog()
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    testConection(id = false) {
      const agent = {}
      if (!id) {
        agent.api_url = this.formDialog.data.api_url
        agent.api_key = this.formDialog.data.api_key
      } else {
        const _agent = this.agents.find(l => l.id == id)
        agent.api_url = _agent.api_url
        agent.api_key = _agent.api_key
      }
      // if agent has api_key add header Authorization
      const headers = {}
      if (agent.api_key) {
        headers.Authorization = `Bearer ${agent.api_key}`
      }
      // test connection to agent
      axios
        .get(`${agent.api_url}/v1/models`, {
          headers: headers
        })
        .then(() => {
          this.$q.notify({
            type: 'positive',
            message: `Agent connection successful.`
          })
        })
        .catch(error => {
          this.$q.notify({
            type: 'negative',
            message: `Agent connection failed. ${error.message}`
          })
        })
    }
  },

  created() {
    this.getAgents()
    this.getApiKeys()
  }
})
