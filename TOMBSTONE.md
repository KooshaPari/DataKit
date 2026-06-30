# TOMBSTONE — DataKit

**Status:** ARCHIVE RECOMMENDED (v37 audit, 2026-06-30)

## Why deprecated

DataKit was absorbed into [`phenotype-python-sdk`](https://github.com/KooshaPari/phenotype-python-sdk)
per commit [`d08cf10`](../../commit/d08cf10) ("DataKit fully absorbed into phenotype-python-sdk (#53)").
A subsequent re-implementation increment (`795f5a1`) added pre-alpha Python scaffolding, but the
repo's work-state remains at 10% / planning-phase with no CI, no coverage gate, no release pipeline,
and no agent-readiness surface — scoring 0.08/3.00 on the v37 41-pillar audit (all 9 of 12 clusters
at 0.00).

The canonical ETL/data-transformation implementation for the Phenotype ecosystem lives in
**`phenotype-python-sdk/packages/data-kit`**.

## Where content moved

| Content | Location |
|---|---|
| Canonical DataKit implementation | [`KooshaPari/phenotype-python-sdk`](https://github.com/KooshaPari/phenotype-python-sdk) — `packages/data-kit` |
| Absorption commits | [`d08cf10`](../../commit/d08cf10), [`c07d284`](../../commit/c07d284), [`ec2a950`](../../commit/ec2a950) |
| Pre-alpha Python scaffold (this repo) | `src/datakit/pipeline.py` — superseded by sdk package |

## Maintainer note

**This repository is recommended for archival.** The maintainer (repo owner) should archive it
via GitHub repository settings → "Archive this repository". No files have been deleted; history
is fully preserved. If standalone DataKit development is restarted, a fresh scaffold from the
Phenotype org templates is recommended rather than continuing from this pre-alpha state.

## Audit reference

- v37 scorecard: [`audits/2026-06-26-v37/DataKit.scorecard.md`](https://github.com/KooshaPari/phenotype-org-audits/blob/main/audits/2026-06-26-v37/DataKit.scorecard.md)
- Overall mean: 0.08 / 3.00 | Factory level: 0 / 4
