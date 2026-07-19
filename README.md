# China, region by region

An interactive map for learning China's regions — what each is known for and how to think about them.

**Live site:** https://yangvincent.com/china-map/

- Real province boundaries (Leaflet + CARTO/OSM tiles), grouped into 8 macro-regions with a HUD info panel
- Overlay toggles: Hu Line, Qinling–Huai line, internal migration flows, terrain hillshade, satellite imagery, Yellow River + Taihang, historical Yellow River courses, Han River + Qinling, story pins, Yangtze + Grand Canal (with Three Gorges reservoir), the treaty century (1839–1911), cuisine clusters, gongfu tea origins, a Three Gorges water-level profile, and the reservoir's real inundation extent at 145 m vs 175 m (flood-filled from pre-dam SRTM elevation data — see `scripts/build_inundation.py`)
- Rivers use real geometry (Natural Earth 10m centerlines via `scripts/build_rivers_js.py`); stylized routes are spline-smoothed
- [RECS.md](RECS.md): per-region watch/read/listen recommendations (with Mandarin-difficulty markers) and a travel shortlist

Built conversationally with Claude Code — the map exposes a `claudeAPI` gesture layer (fly, focus, pulse, caption) so Claude can point at things mid-discussion, and logs clicks so you can ask "what's this one?"
