const mongoose = require('mongoose');

const ClanSchema = new mongoose.Schema({
  tag: String,
  interval: Number,
  previousRun: Date,
  channelId: Number
});

module.exports = mongoose.model('Clan', ClanSchema);