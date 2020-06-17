const axios = require('axios');

module.exports = {
  async battles(tag) {
    
    const options = {
      headers: {
        'Authorization': `Bearer ${process.env.CR_API_TOKEN}`
      }
    };

    try {
      const res = await axios.get(`https://${process.env.CR_API_URL}/players/%23${tag}/battlelog`, options);
      const battles = res.data;
  
      return battles;
    } catch (err) { console.log(`Error: ${err}`) }
    
  }
}