# YouTube Automation Channel Template 🎥🤖

This folder contains a **Blueprinted Scaffold** for launching a NEW automated YouTube channel in any niche (History, Tech, Motivation, Horror, etc.).

## 🚀 Quick Start

1.  **Copy this folder** to a new location (or rename it).
    ```bash
    cp -r channel_template my_new_channel_v1
    cd my_new_channel_v1
    ```

2.  **Setup Configuration**:
    *   Rename `config/config.yaml.example` to `config/config.yaml`.
    *   Edit `niche`, `system_prompt`, and `topics` to match your new channel idea.

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Automation**:
    ```bash
    python3 main_automation.py
    ```

## 📂 Architecture

*   **`modules/script_engine.py`**: Handles AI script generation (OpenAI/Claude).
*   **`modules/media_engine.py`**: Handles finding footage (Pexels) with *Strict Safety Mode* built-in.
*   **`modules/audio_engine.py`**: Handles TTS (ElevenLabs/Google).
*   **`.github/workflows/`**: Contains the auto-pilot scheduler.

## 🛡️ Safety & Reliability

This template inherits the **"Nuclear Safety Protocol"** developed for the original project:
1.  **Strict Visual Mapping**: Uses `thematic_mapping` in config to map abstract concepts to safe visuals.
2.  **No-People Filter**: Automatically appends "no people, nature" to media searches unless configured otherwise.
3.  **Self-healing R&D**: Includes the Trend Manager hook logic.
