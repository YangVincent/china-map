# China, region by region

An interactive map for learning China's regions — what each is known for and how to think about them.

**Live site:** https://yangvincent.github.io/china-map/

- Real province boundaries (Leaflet + CARTO/OSM tiles), grouped into 9 macro-regions with a HUD info panel
- Overlay toggles: Hu Line, Qinling–Huai line, internal migration flows, terrain hillshade, Yellow River + Taihang, historical Yellow River courses, Han River + Qinling
- [RECS.md](RECS.md): per-region watch/read/listen recommendations (with Mandarin-difficulty markers) and a travel shortlist

Built conversationally with Claude Code — the map exposes a `claudeAPI` gesture layer (fly, focus, pulse, caption) so Claude can point at things mid-discussion, and logs clicks so you can ask "what's this one?"
