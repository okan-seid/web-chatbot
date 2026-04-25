let lastCategory = null;
let lastOffset = 0;

const chatBox = document.getElementById("chat-box");

function addMessage(html, sender) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.innerHTML = html;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();

  if (!message) return;

  addMessage(message, "user");
  input.value = "";

  //локален backend
  //const response = await fetch("http://localhost:3000/api/chat", {

  //cloud backend
  const response = await fetch("https://web-chatbot-py3z.onrender.com/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message,
      contextCategory: lastCategory,
      contextOffset: lastOffset
    })
  });

  const data = await response.json();

  if (data.category) {
  lastCategory = data.category;
  }

  if (typeof data.nextOffset === "number") {
  lastOffset = data.nextOffset;
  }

  //само заглавия като линкове
  if (Array.isArray(data.news) && data.news.length > 0) {
    let html = `<div class="news-header"><strong>${data.reply || "Резултати"}</strong></div>`;
    html += `<ul>`;

    data.news.forEach((n) => {
      html += `<li><a href="${n.url}" target="_blank" rel="noopener noreferrer">${n.title}</a></li>`;
    });

    html += `</ul>`;

    addMessage(html, "bot");
    return;
  }

  //само reply като текст
  const safeReply = (data.reply || "Няма резултати.")
    .toString()
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  addMessage(`<strong>${safeReply}</strong>`, "bot");
}

document.getElementById("user-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

window.addEventListener("load", () => {
  if (chatBox.children.length === 0) {
    addMessage(
      "👋 <strong>Добре дошли в уеб чат бота на RazgradNews!</strong><br/><br/>" +
      "Можете да търсите новини по категории например:<br/>" +
      "• <em>Разград</em><br/>" +
      "• <em>криминални</em><br/>" +
      "• <em>България</em><br/>" +
      "• <em>спорт</em><br/>" +
      "• <em>подкасти</em>",
      "bot",
      true
    );
  }
});


