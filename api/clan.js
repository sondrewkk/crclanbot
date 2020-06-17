const axios = require('axios');

module.exports = {
  async members(tag) {
    
    const options = {
      headers: {
        'Authorization': `Bearer ${process.env.CR_API_TOKEN}`
      }
    };

    try {
      const res = await axios.get(`https://${process.env.CR_API_URL}/clans/%23${tag}/members`, options);
      const members = res.data.items;

      return members;
    } catch (err) { console.log(`Error: ${err}`) }
    
  }
}