const axios = require('axios');
const { secrets } = require('docker-secret');

module.exports = {
  async battles(tag) {
    
    const options = {
      headers: {
        'Authorization': `Bearer ${secrets.CR_API_TOKEN || process.env.CR_API_TOKEN}`
      }
    };

    try {
      const res = await axios.get(`https://${process.env.CR_API_URL}/players/%23${tag}/battlelog`, options);
      const battles = res.data;
  
      return battles;
    } catch (err) { console.log(`Error: ${err}`) }
    
  }
}