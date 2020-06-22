const axios = require('axios');

const options = {
  headers: {
    'Authorization': `Bearer ${process.env.CR_API_TOKEN}`
  }
};

module.exports = {
  async members(tag) {
    try {
      const res = await axios.get(`https://${process.env.CR_API_URL}/clans/%23${tag}/members`, options);
      const members = res.data.items;

      return members;
    } catch (err) { console.log(`Error: ${err}`) }
    
  },
  async warlog(tag) {
    try {
      const res = await axios.get(`https://${process.env.CR_API_URL}/clans/%23${tag}/warlog`, options);
      const warlog = res.data.items;

      return warlog;
    } catch (err) { console.log(`Error: ${err}`) }
  }
}