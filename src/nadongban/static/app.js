const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const messages = document.querySelector("#messages");
const memoryCount = document.querySelector("#memory-count");
const clearButton = document.querySelector("#clear");
const voiceButton = document.querySelector("#voice");

function appendMessage(text, role, meta = "") {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  if (role === "bot") {
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "N";
    article.appendChild(avatar);
  }
  const wrapper = document.createElement("div");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrapper.appendChild(bubble);
  if (meta) {
    const detail = document.createElement("div");
    detail.className = "meta";
    detail.textContent = meta;
    wrapper.appendChild(detail);
  }
  article.appendChild(wrapper);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

async function refreshHealth() {
  const response = await fetch("/api/health");
  const data = await response.json();
  memoryCount.textContent = `저장된 기억 ${data.memory_count}개`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  appendMessage(message, "user");
  input.value = "";
  const pending = appendMessage("기억을 검색하고 있어요…", "bot");
  pending.classList.add("loading");
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "요청에 실패했습니다.");
    pending.remove();
    appendMessage(data.answer, "bot", `관련 기억 ${data.retrieved.length}개 검색`);
    memoryCount.textContent = `저장된 기억 ${data.memory_count}개`;
  } catch (error) {
    pending.remove();
    appendMessage(error.message, "bot");
  }
});

clearButton.addEventListener("click", async () => {
  if (!window.confirm("이 브라우저에서 저장한 모든 기억을 삭제할까요?")) return;
  await fetch("/api/memories", {method: "DELETE"});
  memoryCount.textContent = "저장된 기억 0개";
  appendMessage("저장된 기억을 모두 초기화했습니다.", "bot");
});

voiceButton.addEventListener("click", () => {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    appendMessage("이 브라우저는 음성 인식을 지원하지 않습니다.", "bot");
    return;
  }
  const recognition = new Recognition();
  recognition.lang = "ko-KR";
  recognition.onresult = (event) => {
    input.value = event.results[0][0].transcript;
    input.focus();
  };
  recognition.start();
});

refreshHealth().catch(() => {});
