const mongoose = require("mongoose");

const NewsSchema = new mongoose.Schema({
  title: String,
  url: String,
  source: String,
  scraped_at: Date
});

module.exports = mongoose.model("News", NewsSchema);
