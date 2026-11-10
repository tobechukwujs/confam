# Confidence gate: trade-off

> SYNTHETIC fictional pictures only (eval/record.json). Says nothing about real photographs.

Run `2026-11-10T07:22:12+00:00`. 64 honest pictures, 92 edited pictures, 16 crops.

| threshold | honest confirmed | honest false alarms | honest withheld | edits caught (altered) | edits withheld | forged confirmed | crops partial |
|---|---:|---:|---:|---:|---:|---:|---:|
| off | 8 | 30 | 26 | 84 | 8 | 0 | 3 |
| 30 | 8 | 23 | 33 | 82 | 10 | 0 | 3 |
| 40 | 8 | 20 | 36 | 80 | 12 | 0 | 3 |
| 50 | 8 | 18 | 38 | 77 | 15 | 0 | 3 |
| 60 | 8 | 16 | 40 | 73 | 19 | 0 | 3 |
| 65 | 8 | 14 | 42 | 69 | 23 | 0 | 3 |
| 70 | 8 | 11 | 45 | 69 | 23 | 0 | 3 |
| 75 | 8 | 8 | 48 | 68 | 24 | 0 | 3 |
| 80 | 8 | 6 | 50 | 67 | 25 | 0 | 3 |
| 85 | 8 | 6 | 50 | 62 | 30 | 0 | 3 |
| 90 | 8 | 6 | 50 | 61 | 31 | 0 | 3 |
| 95 | 8 | 0 | 56 | 32 | 60 | 0 | 3 |

Confidence of changes reported on honest pictures called altered (noise): `{'n': 47, 'min': 0.0, 'median': 65.0, 'max': 95.0}`.
Lowest confidence among real-fact changes on edited pictures called altered: `{'n': 82, 'min': 0.0, 'median': 93.5, 'max': 96.0}`.
