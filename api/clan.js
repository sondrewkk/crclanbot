const axios = require('axios');
const { api, apiToken } = require('../config.json');

module.exports = {
  async members(tag) {
    
    const options = {
      headers: {
        'Authorization': `Bearer ${apiToken}`
      }
    };

    try {
      const res = await axios.get(`${api}/clans/%23${tag}/members`, options);
      const members = res.data.items;

      return members;
    } catch (err) { console.log(`Error: ${err}`) }
    
  }
}