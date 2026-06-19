# Nature News Walkman

## SKILL简介

`nature-news-walkman` 是一个用于获取 Nature 新闻并整理为英语学习材料的 skill。

它目前支持的能力有这几项：

- 获取 Nature `NEWS` 类型文章的英文原文
- 对候选文章做摘要总结
- 为NEWS文章生成英文朗读音频（mp3）

## 使用边界声明

本项目主要面向**个人学习、英语阅读与听力练习**场景，不面向批量分发、公开镜像、商业转载或绕过来源网站访问限制的用途。

使用时请注意：

- 应遵守 Nature / Springer Nature 及相关来源网站的访问规则、使用条款和版权要求
- 默认应优先使用**公开可见内容**；需要登录态的内容仅应在**用户本人有权访问**的前提下读取
- 通过 `--cookie-file` 提供的登录会话信息仅限**用户本人本地使用**，不应共享、传播或提交到仓库
- 生成的文本、摘要与音频内容应以**个人学习使用**为主，不建议用于公开再分发
- 如平台或网络环境对抓取、TTS 或文件输出有限制，应以实际环境规则为准

## 快速使用

### 1. 如何下载

从 GitHub 下载这个项目，或者直接克隆仓库：

```bash
git clone https://github.com/apeiria-network/nature-news-walkman.git
cd nature-news-walkman
```

如果你不是用 git，也可以直接下载项目压缩包并解压。

### 2. 下载后放到哪里

把 `nature-news-walkman` 这个 skill 文件夹放到你当前平台实际读取 skills 的目录里。不同平台目录不完全一样，但原则是：**放到该平台能识别 slash command / skill 的位置**。

例如：

- **Claude Code / Claude 项目型环境**：通常放在当前项目可被读取的 skills 目录中，例如 `.claude/skills/nature-news-walkman/`
- **你自己维护的自定义 agent / skill 平台**：放到该平台约定的 skills 根目录下，例如 `my-agent-app/skills/nature-news-walkman/`

如果你已经能在当前项目里直接调用 `/nature-news-walkman`，说明放置位置已经正确。

### 3. 用什么命令或提示词触发

你可以直接使用：

```text
/nature-news-walkman
```

也可以在命令后面追加你的要求，例如：

```text
/nature-news-walkman latest neuroscience news
/nature-news-walkman choose easier articles for English learning
/nature-news-walkman climate and health topics
```

### 4. 获取到原文后，LLM 现在能做什么

当前支持：

- 输出英文原文
- 输出摘要总结
- 为你选中的文章生成英文朗读音频

### 5. 朗读音频生成完成后去哪里找

音频通常会保存在当前项目工作目录下的 workspace 子目录中，例如：

- `<workspace>/nature-news-walkman/audio/`

在常见环境里，可能类似：

- `.claude/nature-news-walkman/audio/`
- `.workbuddy/nature-news-walkman/audio/`

如果平台支持文件直接发送，你也可能直接收到 mp3 文件；否则就去上面的音频输出目录查找。

## 脚本说明和常用命令示例

### `scripts/venv_install.sh`

作用：创建 `scripts/.venv` 并安装依赖。

```bash
bash scripts/venv_install.sh
```

### `scripts/rss_fetch.py`

作用：抓取 Nature 当前 RSS，并提取候选文章 URL。

```bash
python scripts/rss_fetch.py
```

### `scripts/fetch_nature_article.py`

作用：抓取文章内容，过滤掉非 `NEWS` 页面，并保存结构化 JSON。

常用示例：

```bash
# 抓单篇文章
python scripts/fetch_nature_article.py --url https://www.nature.com/articles/d41586-026-01923-9

# 从 URL 文件批量抓取
python scripts/fetch_nature_article.py --url-file .claude/nature-news-walkman/tmp/nature_article_urls.txt

# 一次最多抓 5 篇
python scripts/fetch_nature_article.py --url-file .claude/nature-news-walkman/tmp/nature_article_urls.txt --limit 5

# 使用本地 cookie 文件获取更完整正文
python scripts/fetch_nature_article.py --url https://www.nature.com/articles/d41586-026-01903-z --cookie-file .claude/nature-news-walkman/cookie.txt
```

### `scripts/news_read.py`

作用：读取抓取后的文章 JSON，按顺序输出结构化文本，供模型阅读和总结。

```bash
python scripts/news_read.py
```

### `scripts/nature_news_sound.py`

作用：根据文章编号生成英文朗读音频。

输入的编号对应 `news_read.py` 输出里的文章顺序（从 1 开始）。

```bash
# 为第 2 篇生成音频
python scripts/nature_news_sound.py 2

# 为第 2 和第 5 篇生成音频
python scripts/nature_news_sound.py 2 5

# 强制使用 edge-tts
python scripts/nature_news_sound.py 2 --engine edge-tts
```

## skill 工作流程

`nature-news-walkman` 的整体流程是：

1. 准备本地 Python 环境
2. 获取 Nature RSS
3. 提取候选文章链接
4. 抓取文章页面并只保留带 `NEWS` 标识的文章
5. 输出文章原文给模型
6. 由模型先做摘要总结并把候选文章按顺序展示给用户
7. 用户选择想听的文章编号
8. 为选中的文章生成英文朗读音频

也就是说，这个 skill 的设计是：

- **获取候选文章**
- **先输出摘要供用户选择**
- **对选中文章再输出全文 / 音频**

## cookie 使用说明

默认情况下，脚本仅抓取公开可见的页面内容。

当目标文章的部分正文仅对已登录会话可见时，可以通过 `--cookie-file` 向脚本提供一个**本地 cookie 文件**，以便脚本在请求页面时携带该会话信息。

**不建议普通用户使用cookie，这可能伴随一些风险**

例如：

```bash
python scripts/fetch_nature_article.py \
  --url https://www.nature.com/articles/d41586-026-01903-z \
  --cookie-file .claude/nature-news-walkman/cookie.txt
```

`--cookie-file` 指向的文件应来自**用户本人**在浏览器中的有效 Nature 登录会话（[nature.com](https://www.nature.com/)）。该文件通常可通过浏览器开发者工具或本地 cookie 导出工具生成，具体导出方式请参考对应浏览器或工具的官方说明。

注意事项：

- 仅使用**你本人账号**对应的登录会话 cookie
- 仅用于访问**你本人有权查看**的页面内容
- cookie 文件应仅保存在本地，不应共享给他人
- 不要将 cookie 内容直接粘贴到对话、日志或配置文件中
- 不要将 cookie 文件提交到 git，或上传到任何公开仓库
- 如果 cookie 已过期、格式不兼容，或请求未命中有效登录态，脚本将只能获取公开可见内容，或直接抓取失败

## 输出文件说明

运行过程中通常会生成以下内容：

- `<workspace>/nature-news-walkman/tmp/`：RSS 与 URL 列表
- `<workspace>/nature-news-walkman/data/`：抓取后的文章 JSON
- `<workspace>/nature-news-walkman/audio/`：生成的 mp3 音频

## 常见问题

### 为什么有些文章会被跳过？

因为当前只保留带 `NEWS` 标识的 Nature 页面。非 `NEWS` 页面会被自动跳过。

### 为什么抓不到完整全文？

默认只抓公开可见内容。如果文章后半部分需要登录后才能看到，就需要用户自行提供本地 cookie file。

### 为什么批量抓取比较慢？

因为脚本会在多篇文章抓取之间加入 5–10 秒随机延迟，以减少请求过快带来的风险。

### 为什么 gTTS 会失败？

在中国网络环境下，`gTTS` 常常因为无法连接 Google 而失败。这是预期现象。

### 为什么 edge-tts 更稳？

`edge-tts` 不依赖 Google，通常在当前网络环境里更容易成功。

### 音频文件在哪里找？

通常在：

- `<workspace>/nature-news-walkman/audio/`

如果平台支持直接发文件，也可能直接在对话中收到生成的 mp3。

