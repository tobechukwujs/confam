# Evaluation results

Run `2026-11-10T09:33:58+00:00` on commit `c91d503 + uncommitted changes` by `uv run python eval/run.py`.

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
| honest_image | 64 | 8 | 0 | 0 | 56 |
| edits_image | 92 | 32 | 0 | - | - |
| crops_image | 16 | 3 | 0 | - | - |
| **total** | 668 | 537 | 0 | 0 | 56 |

- Forged or invented copies confirmed as genuine: **0** (must be 0).
- Crops confirmed as complete: 0.
- Replaced notice confirmed without `superseded_by`: 0.

## Cases that did not get an accepted verdict

| case | expected | got | changes |
|---|---|---|---|
| `modified_real/00` | altered/not_official | cannot_confirm/not_in_record | - |
| `modified_real/02` | altered/not_official | cannot_confirm/not_in_record | - |
| `honest_image/SEC-E-001/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-001/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-001/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-001/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-001/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-001/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/phone` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-002/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/phone` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-003/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/phone` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-004/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/phone` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-005/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-006/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-006/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-006/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-006/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-006/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-006/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-006/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-007/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-007/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-007/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-007/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-007/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-007/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/clean` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/clean_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/whatsapp` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/whatsapp_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/phone` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/phone_wrapped` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/lowres` | confirmed | cannot_confirm/unclear | - |
| `honest_image/SEC-E-008/lowres_wrapped` | confirmed | cannot_confirm/unclear | - |
| `edits_image/SEC-E-001/date_day/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-001/date_month/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-001/link_host/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-001/link_host/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-001/link_host/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-001/link_host/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/date_day/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/date_day/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/date_day/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/date_day/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/date_month/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/date_month/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/link_host/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/link_host/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/link_host/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-002/link_host/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/date_day/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/date_day/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/date_day/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/date_month/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/date_month/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/time/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/time/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/time/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-003/time/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-004/phone/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-004/phone/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-004/phone/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-004/phone/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-004/negation_removed/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-004/negation_removed/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-005/date_day/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-005/date_day/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-005/date_month/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-005/time/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-005/time/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/link_host/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/link_host/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/link_host/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/link_host/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/number/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/negation_removed/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/negation_removed/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-006/negation_removed/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/date_day/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/date_day/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/date_day/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/date_month/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/link_host/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/link_host/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/link_host/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-007/link_host/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/time/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/time/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/time/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/time/lowres` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/phone/clean` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/phone/whatsapp` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/phone/phone` | altered | cannot_confirm/unclear | - |
| `edits_image/SEC-E-008/phone/lowres` | altered | cannot_confirm/unclear | - |
| `crops_image/SEC-E-001/tail/clean` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-001/tail/whatsapp` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-003/tail/clean` | partial | altered | replace date '12th'->'12th December' |
| `crops_image/SEC-E-003/tail/whatsapp` | partial | altered | replace date '12th'->'12th December' |
| `crops_image/SEC-E-004/tail/clean` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-004/tail/whatsapp` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-005/tail/clean` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-005/tail/whatsapp` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-006/tail/clean` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-006/tail/whatsapp` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-007/tail/clean` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-008/tail/clean` | partial | cannot_confirm/unclear | - |
| `crops_image/SEC-E-008/tail/whatsapp` | partial | cannot_confirm/unclear | - |
