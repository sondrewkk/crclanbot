const axios = require('axios');
const { api, apiToken } = require('../config.json');

module.exports = {
  async battles(tag) {
    
    const options = {
      headers: {
        'Authorization': `Bearer ${apiToken}`
      }
    };

    try {
      const res = await axios.get(`${api}/players/%23${tag}/battlelog`, options);
      const battles = res.data;
  
      return battles;
    } catch (err) { console.log(`Error: ${err}`) }
    
  }
}