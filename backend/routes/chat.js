const express = require("express");
const router = express.Router();
const News = require("../models/News");

const CATEGORY_MAP = [
  { keys: ["криминални", "криминална", "криминално", "крими", "crime", "crimes", "criminal"], category: "kriminalni", label: "🚓 Криминални новини", shortLabel: "Криминални" },
  { keys: ["инциденти", "инцидент", "incidents", "incident"], category: "intsidenti", label: "⚠️ Инциденти", shortLabel: "Инциденти" },
  { keys: ["предстоящо", "предстоящ", "предстоящи", "upcoming"], category: "predstoyashto", label: "📅 Предстоящо", shortLabel: "Предстоящи" },
  { keys: ["разград", "града", "razgrad"], category: "razgrad", label: "🏙️ Новини от Разград", shortLabel: "Разград"},
  { keys: ["областта", "област", "областни", "region", "oblast", "district"], category: "oblastta", label: "🗺️ Областта", shortLabel: "Областта" },
  { keys: ["българия", "bulgaria"], category: "bulgaria", label: "🇧🇬 България", shortLabel: "България" },
  { keys: ["свят", "света", "светът", "world"], category: "svyat", label: "🌍 Свят", shortLabel: "Света"},
  { keys: ["спорт", "спортни", "sport", "sports"], category: "sport", label: "🏅 Спорт", shortLabel: "Спорт" },
  { keys: ["подкасти", "подкаст", "podcast", "podcasts"], category: "podkasti", label: "🎙️ Подкасти", shortLabel: "Подкасти" },
  { keys: ["любопитно", "любопитни", "interesting"], category: "lyubopitno", label: "😄 Любопитно", shortLabel: "Любопитни" },
  { keys: ["гласът", "гласа", "voice"], category: "glasat_na_razgrad", label: "🗞️ Гласът на Разград", shortLabel: "Гласът на Разград" },
  { keys: ["покажи новини", "последни новини", "най-нови новини", "нови новини", "актуални новини", "скорошни новини", "последни", "актуални",
    "latest news", "recent news", "show news", "show latest news", "latest", "recent", "news"], category: "homepage", label: "📰 Последни новини", shortLabel: "Последни" }
];

router.post("/", async (req, res) => {
  try {
    const message = (req.body.message || "").toLowerCase().trim();
    const contextCategory = req.body.contextCategory || null;
    const contextOffset = Number(req.body.contextOffset || 0);

    //Ако няма text input
    if (!message) {
      return res.json({
        reply: "Напиши например: „новини от Разград“, „областта“, „предстоящи“ и др."
      });
    }

    //Ако потребителят иска още новини от последната показана категория
    if (
      message === "дай още" ||
      message === "покажи още" ||
      message === "още" ||
      message === "show more" ||
      message === "more"
    ) {
      if (!contextCategory) {
        return res.json({
          reply: "Няма активна категория. Напиши например: „Покажи Разград/Криминални/Областта...“."
        });
      }

      let query = { category: contextCategory };
      let sort = { rank: 1, scraped_at: -1 };

      //Homepage от featured grid-а
      if (contextCategory === "homepage") {
        sort = { rank: 1, scraped_at: -1 };
      }

      const moreNews = await News.find(query)
        .sort(sort)
        .skip(contextOffset)
        .limit(5);

      if (moreNews.length === 0) {
        return res.json({
          reply: "Няма повече новини в тази категория."
        });
      }

      const categoryInfo = CATEGORY_MAP.find(c => c.category === contextCategory);
      const categoryName = categoryInfo?.shortLabel || contextCategory;

      return res.json({
        reply: `Още новини от ${categoryName}`,
        category: contextCategory,
        nextOffset: contextOffset + moreNews.length,
        news: moreNews.map(n => ({
          title: n.title,
          url: n.url
        }))
          });
    }

    //Намиране категорията по ключови думи
    let matched = null;

    for (const rule of CATEGORY_MAP) {
      const ok = rule.keys.some(k => message.includes(k));
      if (ok) {
        matched = rule;
        break;
      }
    }

    //ако не match-не — показваме примерни категории
    if (!matched) {
      return res.json({
        reply:
          "Не те разбрах 🤖 Опитай: „последни новини“, „спорт“, „криминални“, „инциденти“, „областта“, „подкасти“."
      });
    }

    //Fetch новини по категория
    let query = { category: matched.category };
    let sort = { rank: 1, scraped_at: -1 };

    //за homepage
    if (matched.category === "homepage") {
      sort = { rank: 1, scraped_at: -1 };
    }

    const limit = (matched.category === "homepage") ? 13 : 5;
    console.log("Message:", message);
    console.log("Matched category:", matched.category);

    const news = await News.find(query)
      .sort(sort)
      .skip(0)
      .limit(limit);

    if (news.length === 0) {
      return res.json({ reply: `Няма новини в категория: ${matched.category}` });
    }

    return res.json({
      reply: matched.label,
      category: matched.category,
      nextOffset: news.length,
      news: news.map(n => ({
        title: n.title,
        url: n.url
      }))
    });

  } catch (err) {
    console.error("Chat error:", err);
    return res.status(500).json({ reply: "Възникна грешка в чата." });
  }
});

module.exports = router;