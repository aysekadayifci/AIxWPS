# AI × WPS Integrated v0.6 — Narrative and Debrief Update

## Launch on Mac
1. Unzip this folder under `~/Desktop/Apps/`.
2. `conda activate ai_wps`
3. `cd ~/Desktop/Apps/AI_WPS_Integrated_v07`
4. `python -m pip install -r requirements.txt`
5. `python -m streamlit run app.py`

## Updates
- Expanded technology background, including accuracy validation, subgroup errors, data risks and critical infrastructure dependencies.
- New round-by-round scenario narratives identifying actors, urgent needs and decision goals.
- Detailed humanitarian choice explanations instead of generic prompts.
- More readable high-contrast decision radio cards.
- Decision feedback now includes recorded causal contributors from each choice and institutional reaction, not only aggregate proxy interpretations.
- Next-round preview names the actual crisis and requesting institution and links it to previous decisions and current conditions.
- Camp-wide synthetic demographics: adult women 2,400; adult men 2,000; girls 1,800; boys 1,800. These categories sum to 8,000 and do not encode gender identity or intersectional characteristics.
- Debrief completion now checks the actual history length rather than relying solely on a UI flag.
- Progress JSON available at any time; final HTML, CSV, and JSON reports available after six rounds.
- Ten automated tests pass.

## Caveats
The six crisis milestones remain fixed, although briefings and effects respond to prior choices. Different roles currently share illustrative effect pathways. Sector-level demographics, real-time map changes and fully branching negotiation are not yet simulated. All figures are synthetic educational assumptions.

## v0.6.1 appearance patch
Native Streamlit dark theme plus scoped contrast overrides. Launch from this folder so .streamlit/config.toml is loaded. In browser Settings select Dark or Custom theme if necessary. No engine changes.

## v0.7 Platform entrance and optional AI advisor
Run from this folder: `python -m streamlit run app.py`. The welcome page offers the scenario library and a draft-only custom scenario builder. Ardin is the only playable scenario. Home navigation preserves the session until a new game is launched or restarted.

For optional AI, set `OPENAI_API_KEY` in your local shell before launching. Never share the key or commit it to GitHub. Default model is `gpt-4.1-mini`; override with `OPENAI_MODEL` if needed. API billing is separate. The advisor sends only selected visible game state and your question after explicit opt-in, with store=false. Provider retention policies still apply. No automatic calls, uploads, web retrieval or verified legal citations. Do not send sensitive data. AI analysis does not alter game scores, and custom scenario briefs are not playable. Twelve unit tests pass including mocked API transport; live API and browser appearance not tested here.

## Permanent master installation (0.7.1)
Move the AI_WPS folder to ~/Desktop/Apps once. Launch from that folder using `conda activate ai_wps` and `python -m streamlit run app.py`. Future trusted patch ZIPs are applied with `python update.py ~/Downloads/PATCH.zip` while Streamlit is stopped. The updater validates the source version, stages files, checks Python syntax, backs up changed files, and avoids local data, secrets and uploaded readings. Apply only patches you trust. Existing live sessions are not persisted across restarts. The supplied welcome image and original scenario artwork are bundled for local use; confirm rights to the supplied image before public distribution.
