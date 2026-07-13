# Question content format (v2)

This replaces the old flat CSV schema entirely. Two files:

- **`questions.csv`** — every question.
- **`passages.csv`** — shared comprehension/reading passages that multiple questions can reference (for English comprehension, data-interpretation sets, etc). Optional — most questions won't use one.

Fill these in with a spreadsheet app (Excel, Google Sheets) and export as CSV (UTF-8). One row per question. Don't remove or rename columns — leave a cell blank if it doesn't apply.

## `questions.csv` columns

| Column | Required | Description |
|---|---|---|
| `question_id` | **Yes** | Stable unique ID you assign, e.g. `MTH-0001`. Used to avoid duplicate imports if you re-run the seed script — never reuse an ID for a different question. Suggested convention: `<SUBJECT-CODE>-<NUMBER>` (MTH, ENG, PHY, CHM, BIO, GEO, ECO, LIT, GOV, COM, ACC). |
| `exam_type` | No | `JAMB`, `WAEC`, `NECO`, `POST-UTME`, or blank for general-purpose. |
| `subject` | **Yes** | One of: Mathematics, English, Physics, Chemistry, Biology, Geography, Economics, Literature, Government, Commerce, Accounting. |
| `topic` | **Yes** | Broad topic, e.g. `Algebra`, `Cell Biology`. |
| `subtopic` | No | Finer-grained sub-topic if useful, e.g. `Quadratic Equations`. |
| `difficulty` | **Yes** | `easy`, `medium`, or `hard`. |
| `year` | No | Exam year if this is a real past question, e.g. `2021`. Leave blank for original practice questions — **don't invent a year for a question that isn't actually from that year's paper.** |
| `passage_id` | No | Set this to link the question to a shared passage in `passages.csv` (for comprehension-style questions). Leave blank for standalone questions. |
| `question_text` | **Yes** | The question itself. Plain text; LaTeX-style math is fine if written as `\(...\)` — the frontend can render it later. |
| `image_url` | No | URL to a diagram/graph/figure the question needs. Leave blank if none. |
| `option_a` / `option_b` / `option_c` / `option_d` | **Yes** | The four answer choices. |
| `correct_option` | **Yes** | `A`, `B`, `C`, or `D`. |
| `explanation` | **Yes** | Why the correct answer is correct. This is shown to the student right after they answer — write it like you're teaching, not just stating the answer. |
| `tags` | No | Pipe-separated keywords for search/filtering later, e.g. `equations\|factoring`. |
| `source` | **Yes** | `original` (you/we wrote it), `past-question` (a real transcribed past paper question — only use this if you have the legal right to include it), or `licensed` (from a paid/licensed source). This matters for copyright accountability. |
| `status` | **Yes** | `active` (visible to students) or `draft` (imported but hidden — use this while you're still reviewing a batch). |

## `passages.csv` columns

| Column | Required | Description |
|---|---|---|
| `passage_id` | **Yes** | Matches the `passage_id` used in `questions.csv`. |
| `subject` | **Yes** | Same subject list as above. |
| `title` | No | Short label for the passage (shown above it), e.g. `Comprehension Passage 1`. |
| `passage_text` | **Yes** | The full passage text. |

## Notes

- `questions.csv` and `passages.csv` in this folder currently hold a small set of **sample questions** (a few per subject) demonstrating the format correctly, including a passage-linked question and an image-linked question. These are seeded and working end to end right now.
- To add real content, just append more rows to these same two files (keep the header row, keep `question_id` unique) and re-run `python seed_questions.py` from `backend/`. It's a safe upsert — it only inserts rows whose `question_id` isn't already in the database, so you can grow the bank in batches over time without duplicating or disturbing existing questions or user history.
