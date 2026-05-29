# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.11] - 2026-05-29

### Fixed

- `DocConverter` no longer raises `KeyError('tags')` when processing elements
  returned by the Overpass API without a `tags` field. This happened whenever
  `OSMFetcher` was used without `target_osm_tags` (i.e. querying all node types),
  causing failures in Agent + `ComponentTool` scenarios. Elements without tags are
  now silently skipped, as they carry no useful POI content.
- Fixed a latent guard condition in `_clean_element` where `("lat" or "lon")`
  short-circuited to only checking `"lat"`, leaving elements missing `"lon"`
  undetected.

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
