# Nature News Walkman Vocabulary List Guide

This guide describes how `nature-news-walkman` should generate a learner-friendly vocabulary list for a selected Nature NEWS article.

## Scope

Use this guide when the user asks for a vocabulary list, difficult-word list, new-word notes, or article vocabulary support.

Typical intents:
- generate a vocabulary list for one article
- list difficult words from the selected article
- explain unfamiliar words in the article for study
- make article vocabulary cards for review

The article retrieval and shortlist flow belong in [web_fetch_guide.md](web_fetch_guide.md).
The audio flow belongs in [audio_tts_guide.md](audio_tts_guide.md).
The command and interaction contract belong in [SKILL.md](../SKILL.md).

## When to Generate a Vocabulary List

Generate a vocabulary list only when at least one of these is true:
- the user explicitly asks for a vocabulary list or difficult words
- the user asks for word explanations for a selected article
- the user asks for study notes focused on vocabulary

Do not force a vocabulary list in every run.
By default, the normal flow is still shortlist summary first, then full text and/or audio after user selection.
Vocabulary output is an optional study layer for the chosen article.

## Default Filtering Rule

Use [reference/Oxford_5000.txt](Oxford_5000.txt) as the baseline frequency reference.

Default inclusion rule:
- do **not** include words from CEFR levels `A1`, `A2`, or `B1` as difficult words
- words at `B2`, `C1`, or above may be included when they are useful for learners
- academic or field-specific terms should be included even if they seem common in context

Default exclusion rule:
- do not include very basic function words
- do not include obvious proper names, person names, or place names unless they also function as learnable terms
- do not include the same vocabulary item more than once in the same article list

## Academic and Domain Vocabulary Rule

If a word belongs to an academic, scientific, medical, environmental, technical, or policy-related domain, it should be treated as a candidate difficult word.

Examples of likely candidates:
- hypothesis
- genome
- receptor
- biodiversity
- carbon
- regulation
- microbial

Even if a term looks familiar to advanced readers, include it when it is central to understanding the article.

## Selection Priorities

When the article contains many candidate words, prioritize:
1. words necessary for understanding the article's main idea
2. academic or discipline-specific vocabulary
3. higher-level words with good reuse value
4. words with important multiple meanings
5. words whose morphology helps the learner expand word family knowledge

Avoid producing an excessively long list when a tighter, more useful list is possible.
Prefer a focused study list over mechanical coverage.

## Required Output Fields

Each vocabulary item must include all of the following:
- **单词**: the base form or best learning form
- **词性**: the relevant part of speech in the article context
- **中文词义**: the article-context meaning in Chinese
- **一词多义**: add common extra meanings when the word is polysemous
- **词族 / 变形**: include practical related forms such as plural, tense changes, adjective/adverb/noun/verb derivations when useful
- **例句**: provide one clear English example sentence

## Output Style

Use a **card-style list**, not a markdown table.

Recommended structure:

```md
1. **单词**: hypothesis
   - **词性**: n.
   - **中文词义**: 假设；假说
   - **一词多义**: 在学术写作中常指“待验证的解释或推测”
   - **词族 / 变形**: hypotheses (pl.), hypothetical (adj.), hypothetically (adv.)
   - **例句**: The researchers tested the hypothesis in a series of controlled experiments.
```


Keep the structure consistent across all items.

## Meaning Rules

For Chinese meaning:
- first give the meaning that matches the article context
- then supplement common additional meanings when they are genuinely useful
- do not overload the entry with rare dictionary senses

For polysemy:
- add one or more common meanings when they help the learner avoid misunderstanding
- if the word has a sharply different everyday meaning and article meaning, point that out briefly

## Word Family Rules

Include practical learning forms such as:
- noun plural forms
- verb tense forms when useful
- adjective/adverb/noun/verb derivations
- common related forms used in academic reading

Examples:
- analyze → analyzed, analyzing, analysis, analyst, analytical
- regulate → regulates, regulated, regulating, regulation, regulatory
- species → species

Do not dump every possible derivative.
Include only forms that help learning and recognition.

## Example Sentence Rules

The example sentence should:
- be natural and grammatical English
- be clear enough for an upper-beginner to advanced learner
- preferably reflect the article's topic or scientific context
- avoid being too long or overloaded with jargon

The example may be adapted from the article idea, but should read smoothly as a standalone sentence.

## Phrase Handling

If the real learning unit is a phrase rather than a single word, you may list the phrase as the entry.

Examples:
- result in
- be linked to
- carry out
- in contrast

When doing this, still provide:
- phrase-level meaning in Chinese
- usage-focused example sentence
- relevant form notes if useful

## Ordering Rule

Order the list by learning usefulness, not strict alphabetical order.

Recommended order:
1. core article concepts
2. academic/domain vocabulary
3. reusable advanced general vocabulary
4. helpful phrases

## Quality Guardrails

- Prefer accurate, teachable entries over a long list
- Keep wording concise but informative
- Do not fabricate rare senses just to fill the “一词多义” field
- Do not list A1/A2/B1 words unless there is a strong domain-specific reason
- If a word appears in Oxford A1/A2/B1 but is clearly being used as a specialized academic term, you may still include it and briefly explain why

## Suggested Lead-in

Before the list, the model may add a short line such as:

```md
下面是这篇文章的生词卡片列表。我优先挑选了更值得学习的高阶词和学术词，并默认排除了 Oxford A1-A2-B1 词汇。
```
