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
                  │           MainActivity (Java)             │
                  │  Hosts a single WebView, loads the app    │
                  │  from assets/www/index.html                │
                  └───────────────────┬────────────────────────┘
                                      │
                                      ▼
                  ┌──────────────────────────────────────────┐
                  │     index.html (HTML + CSS + JS)          │
                  │                                            │
                  │  Analyzer → Optimizer → Formatter          │
                  │      → Splitter → Validator                │
                  │                                            │
                  │  All logic runs locally in JavaScript       │
                  └──────────────────────────────────────────┘
```

| Component | Responsibility |
|---|---|
| `MainActivity.java` | Hosts the WebView, configures JS/DOM storage, handles the system back button, and intercepts file downloads (saves to the public Downloads folder via `MediaStore` on Android 10+, legacy file API on Android 9 and below) |
| `assets/www/index.html` | The complete self-contained app — UI plus the full analyzer/optimizer/formatter/splitter/validator pipeline in JavaScript |
| `AndroidManifest.xml` | App metadata, launcher activity declaration, storage permission (scoped to Android ≤ 9 only) |
| `res/mipmap-*` | App icon at all standard Android densities (mdpi → xxxhdpi), including adaptive icon foreground/background layers |
| `res/drawable/splash_background.xml` | Branded splash screen shown while the WebView performs its first paint |

---

## Requirements

- **Android Studio** (Hedgehog or newer recommended) — [download here](https://developer.android.com/studio)
- A device or emulator running **Android 7.0 (API 24) or higher**
- Internet connection on first project sync only (to download the Gradle wrapper and dependencies)

---

## Building the APK

### 1. Open the project
1. Launch Android Studio → **Open** → select the `PromptGeneratorAI-AndroidStudio` folder
2. Allow the initial Gradle sync to complete (downloads the wrapper and dependencies — a few minutes on first run)
3. If prompted to trust the project, click **Trust**

### 2. Build a debug APK (for testing)
**Build → Build Bundle(s) / APK(s) → Build APK(s)**

When the build finishes, click the **locate** link in the notification — do **not** search for the file manually, since the project also generates an unrelated `app-debug-androidTest.apk` (an auto-generated instrumentation test stub, not the real app). The correct file is:

```
app/build/outputs/apk/debug/app-debug.apk
```

### 3. Build a signed release APK (for distribution)
1. **Build → Generate Signed Bundle / APK**
2. Select **APK** → Next
3. Create a new keystore (or use an existing one) — keep the password safe, you'll need it for future updates
4. Select build variant **release** → Finish
5. Output: `app/build/outputs/apk/release/app-release.apk`

### 4. Install on a device
Transfer the APK to an Android phone and tap to install (enable "Install from unknown sources" if prompted).

---

## Project Structure

```
PromptGeneratorAI-AndroidStudio/
├── app/
│   ├── build.gradle                       # App-level config: applicationId, SDK versions, dependencies
│   ├── proguard-rules.pro
│   └── src/main/
│       ├── AndroidManifest.xml            # Permissions, activity & theme declarations
│       ├── java/com/promptgenerator/ai/
│       │   └── MainActivity.java          # WebView host, download handling, back navigation
│       ├── assets/www/
│       │   └── index.html                 # Full app: UI + pipeline logic + embedded icon
│       └── res/
│           ├── layout/activity_main.xml   # WebView + branded loading screen
│           ├── values/                    # Colors, strings, themes
│           ├── drawable/splash_background.xml
│           ├── mipmap-{m,h,x,xx,xxx}hdpi/ # App icon at every density
│           └── mipmap-anydpi-v26/         # Adaptive icon XML (Android 8+)
├── build.gradle                           # Top-level Gradle config
├── settings.gradle
└── gradle.properties
```

---

## Configuration

| Setting | Where | Default |
|---|---|---|
| App name | `res/values/strings.xml` → `app_name` | `Prompt Generator AI` |
| Application ID / package | `app/build.gradle` → `applicationId` | `com.promptgenerator.ai` |
| Version | `app/build.gradle` → `versionCode` / `versionName` | `1` / `3.0.0` |
| Min / Target SDK | `app/build.gradle` | `24` / `34` |
| App icon | `res/mipmap-*/ic_launcher*.png` | Generated from the app logo |
| App content / pipeline logic | `assets/www/index.html` | — |

---

## Permissions

| Permission | Why it's needed |
|---|---|
| `WRITE_EXTERNAL_STORAGE` (capped at API 28) | Lets the "Save File" button write to the public Downloads folder on Android 9 and below. Not required on Android 10+, where the app uses the scoped-storage-compliant `MediaStore` API instead. |

No `INTERNET` permission is requested — the app makes no network calls.

---

## Troubleshooting

**App crashes immediately on open / vanishes from recents**
Check Logcat (`View → Tool Windows → Logcat`, filter by `AndroidRuntime`) for a `FATAL EXCEPTION` block and review the `Caused by:` lines — this is the fastest way to pinpoint a resource or layout issue.

**Installed app shows no icon and won't open**
You likely installed `app-debug-androidTest.apk` instead of `app-debug.apk`. The `-androidTest` file is an auto-generated instrumentation test stub with no UI — uninstall it from Settings → Apps and install the correct file instead.

**APK is unexpectedly small (a few KB)**
Same cause as above — confirm the file name does not contain `androidTest` before installing.

---

## License

Released under the **MIT License**.

## Author

UniversalAI Engineer — engineer@universalprompt.dev
