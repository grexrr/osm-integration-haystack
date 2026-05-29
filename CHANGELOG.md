# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.12] - 2026-05-29

### Fixed

- `DocConverter.read_json` no longer raises when the Overpass API returns a 200
  response with no `elements` field or an empty `elements` list. Both cases now
  produce an empty document list instead of crashing (issue #4).
- `DocConverter` no longer raises `KeyError('tags')` when processing elements
  returned by the Overpass API without a `tags` field. This happened whenever
  `OSMFetcher` was used without `target_osm_tags`, causing failures in Agent +
  `ComponentTool` scenarios. Elements without tags are now silently skipped.
- Fixed a guard condition in `_clean_element` where `("lat" or "lon")` only
  checked `"lat"` due to Python short-circuit evaluation.

### Added

- `OSMFetcher` now enforces `max_token` with a two-phase progressive strategy.
  Phase 1 compresses each document (removes `tags`/`tags_norm` from meta, truncates
  content to 300 chars). Phase 2 drops the farthest documents until within budget.
  Prevents context-window overflows in Agent + `ComponentTool` scenarios (issue #2).

## [0.1.10] - 2026-01-15

### Added

- `GeoRadiusFilter` Haystack component for post-fetch distance filtering.
- `OSMFetcher` supports optional `preset_center` and `preset_radius_m` for
  pipeline use without runtime parameters.

### Changed

- `DocConverter` now filters tags against a frequency-based top-N whitelist to
  reduce document noise.
- `OverpassClient` query builder supports multiple OSM types and tags in a single
  request.
