const EMOJI_STYLES = {
  none: ["", "", ""],
  soft: ["✨", "🌿", "📝"],
  cute: ["💖", "🐻", "🎀"],
  clean: ["✅", "📌", "🧠"],
};

const SECTION_TITLES = ["先说重点", "展开聊聊", "实操建议"];
const DEFAULT_TAGS = ["#小红书文案", "#一键排版", "#内容创作"];

const titleInput = document.querySelector("#title");
const rawTextInput = document.querySelector("#rawText");
const emojiStyleInput = document.querySelector("#emojiStyle");
const hashtagsInput = document.querySelector("#hashtags");
const ctaInput = document.querySelector("#cta");
const resultInput = document.querySelector("#result");
const statusEl = document.querySelector("#status");

function normalizeText(text) {
  return text
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .split("\n")
    .map((line) => line.replace(/[ \t]+/g, " ").trim())
    .filter(Boolean)
    .join("\n");
}

function splitSentences(text) {
  return text
    .replace(/([。！？!?；;])/g, "$1\n")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function splitToSections(items, sectionCount = 3) {
  if (!items.length) {
    return new Array(sectionCount).fill(null).map(() => []);
  }

  const chunk = Math.ceil(items.length / sectionCount);
  return new Array(sectionCount)
    .fill(null)
    .map((_, i) => items.slice(i * chunk, (i + 1) * chunk));
}

function normalizeHashtags(raw) {
  return raw
    .split(/\s+/)
    .map((tag) => tag.trim().replace(/^#+/, ""))
    .filter(Boolean)
    .map((tag) => `#${tag}`);
}

function formatPost(text, title, emojiStyle, rawHashtags, cta) {
  const cleaned = normalizeText(text);
  if (!cleaned) {
    return "";
  }

  const sentences = splitSentences(cleaned);
  const sections = splitToSections(sentences, 3);
  const emojis = EMOJI_STYLES[emojiStyle] || EMOJI_STYLES.soft;
  const blocks = [];

  if (title.trim()) {
    const t = `${emojis[0]} ${title.trim()} ${emojis[0]}`.trim();
    blocks.push(t);
  }

  sections.forEach((section, i) => {
    if (!section.length) return;
    const header = `${emojis[i % emojis.length]} ${SECTION_TITLES[i]}`.trim();
    const body = section.map((line) => `- ${line}`).join("\n");
    blocks.push(`${header}\n${body}`);
  });

  if (cta.trim()) {
    blocks.push(`${emojis[1]} ${cta.trim()}`.trim());
  }

  const allTags = [...DEFAULT_TAGS, ...normalizeHashtags(rawHashtags)];
  blocks.push(allTags.join(" "));

  return `${blocks.join("\n\n")}\n`;
}

function setStatus(text, ok = true) {
  statusEl.textContent = text;
  statusEl.style.color = ok ? "#2b7a0b" : "#d93025";
}

document.querySelector("#formatBtn").addEventListener("click", () => {
  const output = formatPost(
    rawTextInput.value,
    titleInput.value,
    emojiStyleInput.value,
    hashtagsInput.value,
    ctaInput.value,
  );

  if (!output) {
    resultInput.value = "";
    setStatus("请先输入原始文案", false);
    return;
  }

  resultInput.value = output;
  setStatus("排版完成");
});

document.querySelector("#copyBtn").addEventListener("click", async () => {
  if (!resultInput.value.trim()) {
    setStatus("没有可复制内容", false);
    return;
  }

  try {
    await navigator.clipboard.writeText(resultInput.value);
    setStatus("已复制到剪贴板");
  } catch {
    setStatus("复制失败，请手动复制", false);
  }
});

document.querySelector("#clearBtn").addEventListener("click", () => {
  titleInput.value = "";
  rawTextInput.value = "";
  hashtagsInput.value = "";
  resultInput.value = "";
  setStatus("已清空");
});
