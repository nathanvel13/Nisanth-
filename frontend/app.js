const API_BASE = (window.EDUGENIE_CONFIG?.apiBaseUrl || "http://127.0.0.1:8000").replace(/\/$/, "");

const $ = (id) => document.getElementById(id);
const taskEl = $("task");
const inputEl = $("inputText");
const inputLabel = $("inputLabel");
const levelGroup = $("levelGroup");
const weeksGroup = $("weeksGroup");
const countGroup = $("countGroup");
const submitBtn = $("submitBtn");
const btnText = $("btnText");
const spinner = $("spinner");
const resultEl = $("result");
const modelBadge = $("modelBadge");

const config = {
  qa: { label: "Your question", placeholder: "Example: Which is the largest ocean?", button: "Ask EduGenie" },
  explain: { label: "Topic to explain", placeholder: "Example: Explain the Pythagorean theorem for a beginner.", button: "Explain concept" },
  quiz: { label: "Topic or passage", placeholder: "Enter a topic or paste a lesson passage.", button: "Generate quiz" },
  summarize: { label: "Text to summarize", placeholder: "Paste the educational passage here.", button: "Summarize text" },
  learn: { label: "Topic to learn", placeholder: "Example: SQL from beginner to advanced.", button: "Build learning path" }
};

function updateForm() {
  const current = config[taskEl.value];
  inputLabel.textContent = current.label;
  inputEl.placeholder = current.placeholder;
  btnText.textContent = current.button;
  levelGroup.classList.toggle("hidden", taskEl.value === "summarize");
  weeksGroup.classList.toggle("hidden", taskEl.value !== "learn");
  countGroup.classList.toggle("hidden", taskEl.value !== "quiz");
}

taskEl.addEventListener("change", updateForm);
updateForm();

async function readJson(response) {
  const text = await response.text();
  if (!text) return {};
  try { return JSON.parse(text); }
  catch { throw new Error(`Backend returned invalid JSON (HTTP ${response.status}).`); }
}

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    const health = await readJson(response);
    if (!response.ok) throw new Error(health.detail || "Health check failed");
    $("dot").className = "dot good";
    $("statusText").textContent = health.demo_mode ? "Demo mode — API connected" : (health.gemini_configured ? "Gemini ready" : "API connected — key needed");
  } catch (_) {
    $("dot").className = "dot bad";
    $("statusText").textContent = "Backend unavailable";
  }
}
checkHealth();

function renderQuiz(data) {
  resultEl.className = "result";
  const wrapper = document.createElement("div");
  wrapper.className = "quiz-grid";

  data.questions.forEach((q, index) => {
    const card = document.createElement("article");
    card.className = "quiz-card";

    const question = document.createElement("h3");
    question.textContent = `${index + 1}. ${q.question}`;
    card.appendChild(question);

    const feedback = document.createElement("p");
    feedback.className = "feedback";
    feedback.hidden = true;

    q.options.forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "quiz-option";
      button.textContent = option;
      button.addEventListener("click", () => {
        card.querySelectorAll(".quiz-option").forEach((item) => item.classList.remove("correct", "incorrect"));
        if (option === q.correct_answer) button.classList.add("correct");
        else {
          button.classList.add("incorrect");
          card.querySelectorAll(".quiz-option").forEach((item) => {
            if (item.textContent === q.correct_answer) item.classList.add("correct");
          });
        }
        feedback.textContent = `Correct answer: ${q.correct_answer}${q.explanation ? ` — ${q.explanation}` : ""}`;
        feedback.hidden = false;
      });
      card.appendChild(button);
    });

    card.appendChild(feedback);
    wrapper.appendChild(card);
  });

  resultEl.replaceChildren(wrapper);
}

async function submit() {
  const text = inputEl.value.trim();
  if (!text) {
    resultEl.className = "result error";
    resultEl.textContent = "Please enter a question, topic, or passage first.";
    return;
  }

  const task = taskEl.value;
  const body = { text };
  if (task === "qa") body.level = $("level").value;
  if (task === "learn") { body.level = $("level").value; body.weeks = Number($("weeks").value); }
  if (task === "quiz") body.count = Number($("count").value);

  const endpoint = task === "learn" ? "/learn/recommendations" : `/${task}`;
  submitBtn.disabled = true;
  spinner.classList.remove("hidden");
  resultEl.className = "result";
  resultEl.textContent = "EduGenie is thinking…";
  modelBadge.classList.add("hidden");

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const payload = await readJson(response);
    if (!response.ok) throw new Error(payload.detail || payload.error || `Request failed (HTTP ${response.status}).`);
    if (task === "quiz") renderQuiz(payload);
    else {
      resultEl.className = "result";
      resultEl.textContent = payload.result || "No result returned.";
    }
    if (payload.model) {
      modelBadge.textContent = `Model: ${payload.model}`;
      modelBadge.classList.remove("hidden");
    }
  } catch (error) {
    resultEl.className = "result error";
    resultEl.textContent = error.message || "Request failed.";
  } finally {
    submitBtn.disabled = false;
    spinner.classList.add("hidden");
  }
}

submitBtn.addEventListener("click", submit);
inputEl.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") submit();
});
