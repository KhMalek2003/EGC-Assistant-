const API_URL = "http://127.0.0.1:8000/chat";

const messagesEl = document.getElementById("chat-messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("chat-input");

let conversation = [];

// Ajoute un message dans l'UI
function addMessage(role, content) {
  const div = document.createElement("div");
  div.classList.add("message", role);
  div.textContent = content;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// Message de bienvenue
addMessage(
  "assistant",
  "Bonjour 👋 Je suis EGC BOT, l’assistant d’EGC Interim. Comment puis-je vous aider ?"
);
conversation.push({
  role: "assistant",
  content:
    "Bonjour 👋 Je suis EGC BOT, l’assistant d’EGC Interim. Comment puis-je vous aider ?",
});

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;

  // Ajout message utilisateur
  addMessage("user", text);
  conversation.push({ role: "user", content: text });
  inputEl.value = "";
  inputEl.focus();
  formEl.querySelector("button").disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ messages: conversation }),
    });

    if (!response.ok) {
      throw new Error("Erreur HTTP " + response.status);
    }

    const data = await response.json();
    const botReply = data.reply || "(Pas de réponse du serveur)";

    addMessage("assistant", botReply);
    conversation.push({ role: "assistant", content: botReply });
  } catch (err) {
    console.error(err);
    addMessage(
      "assistant",
      "Désolé, une erreur technique est survenue. Merci de réessayer plus tard."
    );
  } finally {
    formEl.querySelector("button").disabled = false;
  }
});
