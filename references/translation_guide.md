# Nature News Bilingual Translation Reference

## Translation Style Guide

### General Principles
- Translate sentence by sentence, preserving paragraph structure
- One English line followed by one Chinese translation line
- Keep technical terms accurate; add Chinese equivalent in parentheses on first occurrence
- Preserve proper nouns (names, institutions) in original English

### Common Scientific Terms (Examples)

| English | Chinese |
|---------|---------|
| cellular reprogramming | 细胞重编程 |
| partial reprogramming | 部分重编程 |
| glaucoma | 青光眼 |
| optic nerve | 视神经 |
| neuron regeneration | 神经元再生 |
| gene therapy | 基因疗法 |
| base editing | 碱基编辑 |
| CRISPR-Cas9 | CRISPR-Cas9 |
| nucleation | 成核 |
| homogeneous nucleation | 均匀成核 |
| heterogeneous nucleation | 非均匀成核 |
| classical nucleation theory (CNT) | 经典成核理论 |
| mosaicism | 镶嵌性 |
| in vitro fertilization (IVF) | 体外受精 |
| preprint | 预印本 |
| peer review | 同行评审 |
| stem cell | 干细胞 |
| sickle-cell disease | 镰状细胞病 |
| haemoglobin | 血红蛋白 |

### Formatting Rules
- **Article headers**: `## Article N: [English Title]`
- **Bilingual metadata**: One EN line, one CN line (e.g., Title / 标题, Author / 作者)
- **Sub-headings**: `#### English Heading / 中文标题`
- **Quotes**: Translate the quote and attribute in Chinese
- **Credits/DOI**: Keep in original English

## TTS Guidelines

### Local Python Environment
- Always prefer the existing `.venv` under the skill root before generating audio
- A reusable local `.venv` must use Python **3.10–3.14**
- If the local `.venv` is missing required dependencies, install the missing dependencies into **that same `.venv`**
- If no suitable local `.venv` exists, create `.venv` under the skill root with Python **3.10–3.14**
- Install all runtime dependencies only into the skill-local `.venv`
- Do **not** install dependencies into system Python, global site-packages, user site-packages, or any environment outside the skill root

### Text Preparation for TTS
1. Remove markdown formatting (*, **, #, etc.)
2. Remove credit lines ("Credit: ...")
3. Remove image references
4. Expand abbreviations on first mention in spoken form
5. Clean up special characters that TTS engines may mispronounce

### TTS Engine Selection

| Engine | Priority | Network | Quality | Notes |
|--------|----------|---------|---------|-------|
| **gTTS** | Primary (1st) | Needs Google access | Medium | Fast, simple; fails in China without VPN |
| **edge-tts** | Fallback (2nd) | No VPN needed | Good | Microsoft Edge neural voices; works in China |

**Auto-fallback logic:** Try gTTS first -> if it fails -> automatically switch to edge-tts.

### gTTS Usage (Primary)

```python
from gtts import gTTS
tts = gTTS(text=article_text, lang='en', slow=False)
tts.save('output.mp3')
```

- `lang='en'` for English
- `lang='zh-CN'` for Mandarin Chinese
- `slow=False` for natural reading speed
- Typical output: ~1.7 MB for a 3-4 minute article

### edge-tts Usage (Fallback)

```python
import edge_tts
import asyncio

VOICE_MAP = {
    'en': 'en-US-AvaNeural',        # Female, US English
    'en-GB': 'en-GB-SoniaNeural',   # Female, British English
    'zh-CN': 'zh-CN-XiaoxiaoNeural', # Female, Mandarin Chinese
}

async def generate(text, output_path, voice='en-US-AvaNeural'):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

asyncio.run(generate(cleaned_text, 'output.mp3'))
```

- Install inside the skill-local `.venv` only
- List available voices: `edge-tts --list-voices`
- Typical output: ~2-3 MB for a 3-4 minute article
- Advantage: No Google dependency, works in mainland China

### Using the Unified Interface

```python
from scripts.nature_digest import generate_tts_audio

# Auto mode: gTTS -> edge-tts fallback
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='auto')

# Force specific engine
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='edge-tts')
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='gtts')
```

- `generate_tts_audio(...)` will first prepare the skill-local `.venv`
- It reuses `.venv` when the Python version is 3.10–3.14 and installs any missing required dependencies into that same environment
- It does not use or modify Python environments outside the skill root

## Nature News Page Structure

### URL Patterns
- News index: `https://www.nature.com/news`
- Individual article: `https://www.nature.com/articles/d41586-XXXX-XXXXX-X`
- Volume/Issue: `https://www.nature.com/nature/volumes/{vol}/issues/{issue}`

### Article Extraction
- **Title**: Usually in `<h1>` or prominent heading
- **Author**: Listed after title, sometimes with affiliations
- **Date**: Format "DD Month YYYY"
- **Body**: Sequential paragraphs; may be partially paywalled
- Extract all freely visible content; note paywall limitations
