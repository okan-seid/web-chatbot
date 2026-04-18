const express = require("express");
const router = express.Router();
const News = require("../models/News");

//последни новини
router.get("/", async (req, res) => {
  const news = await News.find()
    .sort({ scraped_at: -1 })
    .limit(10);

  res.json(news);
});

//търсене по ключова дума
router.get("/search", async (req, res) => {
  const q = req.query.q || "";

  const news = await News.find({
    title: { $regex: q, $options: "i" }
  }).limit(10);

  res.json(news);
});

router.get("/category/:category", async (req, res) => {
  try {
    const { category } = req.params;

    const news = await News.find({ category })
      .sort({ publishedAt: -1 })
      .limit(10);

    res.json(news);
  } catch (err) {
    res.status(500).json({ error: "Грешка при зареждане на новини" });
  }
});

module.exports = router;
