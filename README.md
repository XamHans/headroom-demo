# Headroom Video Demo

> **Want the code, walkthroughs, and practical AI engineering systems behind these demos?**
> Join **[The AI Engineer](https://www.skool.com/ai-builders-6997)** — my Skool community for developers building real AI systems.

![The AI Engineer community](https://assets.skool.com/f/1d996b4fb16c47b188ef65bda1e70d1c/227f992762bf4bd99c1fd91dc62d0737ed72c12eef0742669afdccd59f4c857a.jpg)

This repository contains the demo assets for a YouTube video about Headroom — a local-first context compression layer for AI agents.

If you want the code, walkthroughs, and practical AI engineering systems behind these demos, join my Skool community: [The AI Engineer](https://www.skool.com/ai-builders-6997).

It focuses on a practical question:

How do you make long tool outputs, logs, JSON, and conversation context smaller without losing the signal that matters?

The notebook now includes a live OpenAI call so the API key from `.env` is used concretely, not just stored.

## What is inside

- `headroom_erklaerung_de.ipynb` — German notebook: before/after demo with live OpenAI call, latency and token metrics
- `headroom_explanation_en.ipynb` — English version of the same notebook
- `.env.example` — safe template for local secrets
- `pyproject.toml` — uv project setup for the demo

## Why this demo exists

The goal is to make Headroom easy to understand in a video format:

- what Headroom does
- where it sits in the pipeline
- how the three usage modes differ
- what you can control when trimming context
- how many tokens you save in a before/after comparison

## Setup

1. Copy the env template:

```bash
cp .env.example .env
```

2. Add your OpenAI key to `.env`:

```env
OPENAI_API_KEY=your-key-here
```

3. Install dependencies:

```bash
uv sync
```

This creates `.venv` and installs everything from `pyproject.toml`.

4. Run the notebook:

**VS Code** (recommended — no extra steps):
- Install the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
- Open `headroom_erklaerung_de.ipynb`
- Select kernel: `.venv (Python 3.11+)` from the kernel picker

**Terminal / browser:**

```bash
uv run jupyter notebook headroom_erklaerung_de.ipynb
```

This opens the notebook in your browser using the uv-managed environment.

## Secrets policy

- `.env` stays local and must never be committed
- `.env.example` is safe to commit
- `.venv/` is ignored

## Community context

This demo is also meant to support my Skool community, **The AI Engineer**, where I share practical AI engineering workflows, demos, and systems that turns you into a high paying AI engineer role.

## Recommended use in the video

Use the notebook to show:

1. raw context before Headroom
2. compressed context after Headroom
3. token savings and the key parameters that control trimming

That keeps the story concrete instead of theoretical.
