# 🧫 Bacterial Identification Assistant

[![Live App](https://img.shields.io/badge/Live%20Demo-Streamlit-1f6f6b?style=for-the-badge)](https://bacterial-identification-assistant-60578.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

An educational decision-support tool that identifies bacteria from Gram stain,
morphology, and biochemical test results — built to bridge classroom
Clinical Bacteriology with hands-on software development.

**🔗 Try it live:** https://bacterial-identification-assistant-60578.streamlit.app/

---

## Screenshot

<!-- Replace this with an actual screenshot: drag an image into this spot on GitHub,
     or run the app, take a screenshot, save it to /screenshots, and reference it below. -->
![App screenshot](<img width="1916" height="905" alt="Screenshot 2026-08-21 8 39 51 AM" src="https://github.com/user-attachments/assets/6cccf6cc-24b9-4129-baf3-3971d4ee6f5e" />
)

---

## What it does

- **Rule-based identification** — enter Gram stain, shape, arrangement, and up
  to 7 biochemical test results (catalase, coagulase, oxidase, indole, urease,
  citrate, motility) and get a ranked match against a reference database of
  9 clinically relevant organisms.
- **Transparent scoring** — every match shows exactly which tests agreed and
  which didn't, so the result is never a black box. The score reflects
  agreement with the reference database only, not a diagnostic confidence
  level.
- **Practice Mode** — generates a random "unknown organism" case with partial
  lab results so students can self-test their identification skills.
- **Optional AI explanation** — after the rule-based engine determines a
  result, an LLM (via the Groq API) can explain *why* those characteristics
  point to that organism, in plain student-friendly language. The AI never
  identifies anything itself — it only explains an answer that was already
  computed deterministically, and the app works fully without it if the API
  is unavailable.

## Why this project

Built as a BS Medical Laboratory Technology student project to combine two
skill sets: applying real Clinical Bacteriology identification logic (the
same characteristics used at the bench), and structuring a maintainable
Python codebase with a clear separation between data, logic, and UI.

## Tech stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| Data | Pandas + a CSV reference database |
| Optional AI explanation | [Groq API](https://groq.com/) (Llama/OSS models) |
| Hosting | Streamlit Community Cloud |

## Project structure

```
bacterial-identification-assistant/
├── app.py                    # Streamlit UI — inputs, results, styling
├── data/
│   └── bacteria.csv          # Reference database: 9 organisms × 10 tests
├── utils/
│   ├── identification.py     # Scoring/matching engine (no UI code)
│   └── ai_explain.py         # Optional Groq-powered explanation layer
├── requirements.txt
├── README.md
└── screenshots/
```

## Running it locally

```bash
git clone https://github.com/zee5969/Bacterial-Identification-Assistant.git
cd Bacterial-Identification-Assistant
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

To enable the optional AI explanation layer locally, create
`.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-key-here"
```

## Known limitations

- The reference database currently covers 9 organisms and 10 characteristics.
  Some clinically important differentiating tests (novobiocin susceptibility,
  hemolysis pattern, optochin sensitivity) aren't included yet, so a couple
  of closely related organisms (e.g. *S. epidermidis* vs. *S. saprophyticus*)
  may return tied scores.
- This tool is **for educational use only**. It is not a validated diagnostic
  system and is not a substitute for laboratory procedures, professional
  interpretation, or clinical diagnosis.

## Roadmap

- [ ] Add novobiocin, hemolysis, and optochin tests
- [ ] Expand the organism database
- [ ] Add a decision-tree style visualization of the identification path
- [ ] Export results as a printable lab worksheet

## Author

**Zeeshan Ali**
BS Medical Laboratory Technology · Riphah International University

---

*⚠️ This tool is for educational purposes only and does not replace
professional laboratory procedures or clinical diagnosis.*
