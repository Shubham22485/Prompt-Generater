# Prompt Generator AI — Android App

> Turns rough instructions into structured, production-ready AI prompts — right on your phone, fully offline.

[![Platform: Android](https://img.shields.io/badge/platform-Android-3DDC84.svg)](app/build.gradle)
[![Min SDK: 24](https://img.shields.io/badge/minSdk-24%20(Android%207.0)-blue.svg)](app/build.gradle)
[![Target SDK: 34](https://img.shields.io/badge/targetSdk-34%20(Android%2014)-blue.svg)](app/build.gradle)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

---

## Overview

**Prompt Generator AI** is a native Android wrapper around the *Universal Prompt Optimizer* engine. Give it a short, informal request — like *"write a python script to parse CSV files"* — and it runs the request through a five-stage pipeline to produce a structured, professional prompt ready to paste into any LLM:

1. **Analyze** — detects target language, framework, platform, and required features (file I/O, network, database, auth, concurrency, encryption)
2. **Optimize** — expands the request into 8–13 structured sections (Objective, Role, Task, Requirements, Workflow, Quality Standards, Error Handling, Edge Cases, etc.)
3. **Format** — renders the result as Markdown, JSON, or plain text
4. **Split** — automatically breaks oversized output into numbered, continuation-tagged parts at natural section boundaries
5. **Validate** — runs a self-review pass for placeholders, missing sections, and risky code patterns before delivery

The entire pipeline runs as **local JavaScript inside an Android WebView** — there is no backend, no API calls, and no internet permission. Everything happens on-device.

---

## Features

- 🔍 Automatic language & framework detection (Python, JavaScript/TypeScript, Rust, Go, Java, C++, C#, Swift, Ruby, PHP and common frameworks)
- 🧩 Feature-aware analysis (file I/O, networking, database, auth, UI, API, concurrency, encryption)
- 📋 Gap detection — flags missing details and fills them with labeled assumptions instead of guessing silently
- 📚 Per-language library suggestions
- 📦 Three output formats: Markdown, JSON, plain text
- ✂️ Smart auto-splitting for long output
- ✅ Built-in validation pass with a pass/fail score
- 💾 Save results directly to the device's **Downloads** folder
- 📋 One-tap copy to clipboard
- 🌙 Dark, neon-accented UI matching the app icon
- 🔒 100% on-device — no network calls, no telemetry, no data collection

---

## How It Works

```
                  ┌──────────────────────────────────────────┐
                  │           MainActivity (Java)            │
                  │  Hosts a single WebView, loads the app   │
                  │  from assets/www/index.html              │
                  └───────────────────┬──────────────────────┘
                                      │
                                      ▼
                  ┌──────────────────────────────────────────┐
                  │     index.html (HTML + CSS + JS)         │
                  │                                          │
                  │  Analyzer → Optimizer → Formatter        │
                  │      → Splitter → Validator              │
                  │                                          │
                  │  All logic runs locally in JavaScript    │
                  └──────────────────────────────────────────┘
```

## Permissions

| Permission | Why it's needed |
|---|---|
| `WRITE_EXTERNAL_STORAGE` (capped at API 28) | Lets the "Save File" button write to the public Downloads folder on Android 9 and below. Not required on Android 10+, where the app uses the scoped-storage-compliant `MediaStore` API instead. |

No `INTERNET` permission is requested — the app makes no network calls.

---

## License

Released under the **MIT License**.
