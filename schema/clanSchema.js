const mongoose = require('mongoose');

const ClanSchema = new mongoose.Schema({
  tag: String,
  interval: Number,
  previousRun: { type: Date, default: 0},
  channelId: String
});

module.exports = mongoose.model('Clan', ClanSchema);