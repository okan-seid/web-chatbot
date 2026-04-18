require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

//Онлайн база MongoDB Atlas
mongoose.connect(process.env.MONGO_URI)
//mongoose.connect("mongodb://localhost:27017/web-chatbot")
  .then(() => console.log("MongoDB connected"))
  .catch(err => console.error(err));

app.use("/api/news", require("./routes/news"));
app.use("/api/chat", require("./routes/chat"));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
