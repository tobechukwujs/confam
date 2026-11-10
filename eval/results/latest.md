# Evaluation results

Run `2026-11-10T09:17:31+00:00` on commit `10c8ce9 + uncommitted changes` by `uv run python eval/run.py`.

> SYNTHETIC. Every case is built from the fictional Simulated Electoral Commission record in eval/record.json. These numbers say nothing about real notices, real letterheads or stamps, or real photographs.

| suite | cases | correct | forged confirmed | false alarms | honest not confirmed |
|---|---:|---:|---:|---:|---:|
| honest_text | 168 | 168 | 0 | 0 | 0 |
| edits_text | 131 | 131 | 0 | - | - |
| edits_text_wrapped | 131 | 131 | 0 | - | - |
| crops_text | 24 | 24 | 0 | - | - |
| invented | 15 | 15 | 0 | - | - |
| modified_real | 3 | 1 | 0 | - | - |
| paraphrases | 4 | 4 | 0 | - | - |
| pidgin_rumours | 20 | 20 | 0 | - | - |
| honest_image | 64 | 8 | 0 | 30 | 26 |
| edits_image | 92 | 84 | 0 | - | - |
| crops_image | 16 | 3 | 0 | - | - |
| **total** | 668 | 589 | 0 | 30 | 26 |

- Forged or invented copies confirmed as genuine: **0** (must be 0).
- Crops confirmed as complete: 0.
- Replaced notice confirmed without `superseded_by`: 0.

## Cases that did not get an accepted verdict

| case | expected | got | changes |
|---|---|---|---|
| `modified_real/00` | altered/not_official | cannot_confirm/not_in_record | - |
| `modified_real/02` | altered/not_official | cannot_confirm/not_in_record | - |
| `honest_image/SEC-E-001/clean` | confirmed | altered | insert number '9'->None |
| `honest_image/SEC-E-001/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-001/whatsapp_wrapped` | confirmed | altered | delete text None->'on' |
| `honest_image/SEC-E-001/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-001/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-001/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/phone` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/phone_wrapped` | confirmed | altered | insert number '0'->None |
| `honest_image/SEC-E-002/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/whatsapp` | confirmed | altered | insert number '2'->None; insert text 'M'->None |
| `honest_image/SEC-E-003/whatsapp_wrapped` | confirmed | altered | insert number '2'->None; insert text 'M'->None |
| `honest_image/SEC-E-003/phone` | confirmed | altered | replace time '2:00 '->'2:00 pm'; insert text 'P'->None |
| `honest_image/SEC-E-003/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/lowres` | confirmed | altered | insert number '2'->None; insert text 'M'->None |
| `honest_image/SEC-E-003/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/phone` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/clean` | confirmed | altered | insert number '4'->None; insert text 'M'->None |
| `honest_image/SEC-E-005/clean_wrapped` | confirmed | altered | insert text 'M'->None |
| `honest_image/SEC-E-005/whatsapp` | confirmed | altered | insert text 'M'->None |
| `honest_image/SEC-E-005/whatsapp_wrapped` | confirmed | altered | replace text 'YOUF'->'your' |
| `honest_image/SEC-E-005/phone` | confirmed | altered | insert number '4'->None; delete text None->'can'; replace text 'YOU'->'your'; insert text 'M'->None |
| `honest_image/SEC-E-005/phone_wrapped` | confirmed | altered | replace time '4:00 '->'4:00 pm'; insert text 'P'->None |
| `honest_image/SEC-E-005/lowres` | confirmed | altered | insert text 'M'->None |
| `honest_image/SEC-E-005/lowres_wrapped` | confirmed | altered | insert text 'M'->None |
| `honest_image/SEC-E-006/clean` | confirmed | altered | delete text None->'on'; replace text 'OF'->'or' |
| `honest_image/SEC-E-006/clean_wrapped` | confirmed | altered | delete text None->'on'; replace text 'OF'->'or' |
| `honest_image/SEC-E-006/whatsapp` | confirmed | altered | delete text None->'on'; replace text 'Of'->'or' |
| `honest_image/SEC-E-006/whatsapp_wrapped` | confirmed | altered | replace text 'OF'->'or' |
| `honest_image/SEC-E-006/phone_wrapped` | confirmed | altered | insert number '0'->None; delete text None->'on' |
| `honest_image/SEC-E-006/lowres` | confirmed | altered | delete text None->'on' |
| `honest_image/SEC-E-006/lowres_wrapped` | confirmed | altered | delete text None->'on' |
| `honest_image/SEC-E-007/clean` | confirmed | altered | replace text 'N'->'on' |
| `honest_image/SEC-E-007/clean_wrapped` | confirmed | altered | replace text 'N'->'on' |
| `honest_image/SEC-E-007/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-007/whatsapp_wrapped` | confirmed | altered | replace text 'Pel'->'per'; replace text 'N'->'on' |
| `honest_image/SEC-E-007/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-007/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/clean` | confirmed | altered | insert number '4'->None |
| `honest_image/SEC-E-008/clean_wrapped` | confirmed | altered | insert number '4'->None; replace text 'NyOne'->'anyone' |
| `honest_image/SEC-E-008/whatsapp` | confirmed | altered | insert text 'M'->None |
| `honest_image/SEC-E-008/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/phone` | confirmed | altered | insert number '4'->None; delete text None->'are' |
| `honest_image/SEC-E-008/phone_wrapped` | confirmed | altered | insert number '4'->None; delete text None->'are' |
| `honest_image/SEC-E-008/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `edits_image/SEC-E-001/link_host/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/link_host/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-004/phone/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-004/phone/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/link_host/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/link_host/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/link_host/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/time/whatsapp` | altered | cannot_confirm/unclear | - |
| `crops_image/SEC-E-001/tail/clean` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-001/tail/whatsapp` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-003/tail/clean` | partial | altered | replace date '12th'->'12th December' |
| `crops_image/SEC-E-003/tail/whatsapp` | partial | altered | replace date '12th'->'12th December' |
| `crops_image/SEC-E-004/tail/clean` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-004/tail/whatsapp` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-005/tail/clean` | partial | altered | insert number '4'->None; insert text 'M'->None |
| `crops_image/SEC-E-005/tail/whatsapp` | partial | altered | insert number '2'->None; replace text 'YOU'->'your'; insert text 'M'->None |
| `crops_image/SEC-E-006/tail/clean` | partial | altered | delete text None->'on' |
| `crops_image/SEC-E-006/tail/whatsapp` | partial | altered | delete text None->'on' |
| `crops_image/SEC-E-007/tail/clean` | partial | altered | replace text 'N'->'on' |
| `crops_image/SEC-E-008/tail/clean` | partial | altered | insert number '4'->None |
| `crops_image/SEC-E-008/tail/whatsapp` | partial | cannot_confirm/unclear | - |
