# Nature News Digest - Conversation Output Template

## Brief Mode Template

```
News {N}: {English Title}

Publication Date: {Date in English}
Source: {URL}

Summary
{120-180 word English summary}

[Optional Chinese Notes]
{Chinese key points only if the user asked for them}
```

## Text Mode Template

```
News {N}: {English Title}

Publication Date: {Date in English}
Source: {URL}

Full English Text
{Full original English text from the news page}

[Optional Chinese Notes]
{Chinese key points / Chinese explanation only if the user asked for them}
```

## Sound Mode Template

```
News {N}: {English Title}

Publication Date: {Date in English}
Source: {URL}

Full English Text
{Full original English text from the news page}

[Optional Chinese Notes]
{Chinese key points / Chinese explanation only if the user asked for them}

Audio
Nature_Article{N}_English.mp3
```

## Shared Notes

- Deliver the text result directly in the conversation
- Do not write the text result to a markdown file
- Treat the 3 commands as parallel output modes: `brief`, `text`, and `sound`
- Reuse the same latest Nature news batch across modes when cache reuse is appropriate
- Keep the user's original trailing text requirements available for later mode switches
- TTS audio (English): `Nature_Article{N}_English.mp3`

## Output Checklist

- [ ] Determine whether the user asked for `brief`, `text`, or `sound`
- [ ] Preserve the user's trailing text requirements
- [ ] Search Nature latest news or reuse the latest cached news batch
- [ ] Fetch full English text for each selected news item when needed
- [ ] Output the correct mode-specific result structure
- [ ] Generate TTS audio only for `sound`
- [ ] Verify generated audio files exist and are non-empty when audio is requested
