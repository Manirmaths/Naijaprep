import argparse
import csv
import re
from pathlib import Path

import pdfplumber


DEFAULT_PDF = Path(r"C:\Users\Dell\Downloads\JAMB Mathematics Past Questions 1983 - 2004.pdf")
DEFAULT_OUT = Path("data/staging/mathematics_1983_2004_pdf_extracted.csv")

YEAR_RE = re.compile(r"\bMathematics\s+((?:19|20)\d{2})\b", re.IGNORECASE)
OPTION_RE = re.compile(r"(?<![A-Za-z0-9])([A-E])\.\s*")
QUESTION_NUM = r"(?:[1-9]|[1-4]\d|50)"


def match_question_start(line: str):
    punctuated = re.match(rf"^\s*\??\s*(?P<num>{QUESTION_NUM})[.)]\s*(?P<rest>.*)$", line)
    if punctuated:
        return int(punctuated.group("num")), punctuated.group("rest").strip()

    two_digit_standalone = re.match(r"^\s*(?P<num>1[0-9]|[2-4][0-9]|50)\s*$", line)
    if two_digit_standalone:
        return int(two_digit_standalone.group("num")), ""

    two_digit_text = re.match(r"^\s*(?P<num>1[0-9]|[2-4][0-9]|50)\s+(?P<rest>(?=[A-Z(0-9#]).*)$", line)
    if two_digit_text:
        return int(two_digit_text.group("num")), two_digit_text.group("rest").strip()

    one_digit_text = re.match(r"^\s*(?P<num>[1-9])\s+(?P<rest>(?=[A-Z(]).*)$", line)
    if one_digit_text:
        return int(one_digit_text.group("num")), one_digit_text.group("rest").strip()

    return None


def clean_text(value: str) -> str:
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\s+\n", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def iter_heading_positions(pdf):
    headings = []
    for page_index, page in enumerate(pdf.pages):
        words = page.extract_words(x_tolerance=1, y_tolerance=3) or []
        lines: dict[float, list[dict]] = {}
        for word in words:
            y = round(word["top"] / 3) * 3
            lines.setdefault(y, []).append(word)

        for y, line_words in sorted(lines.items()):
            text = " ".join(word["text"] for word in sorted(line_words, key=lambda word: word["x0"]))
            match = YEAR_RE.search(text)
            if match:
                headings.append((page_index, y, match.group(1)))
    return headings


def extract_band_text(page, top: float, bottom: float) -> str:
    mid = page.width / 2
    parts = []
    for x0, x1 in ((0, mid), (mid, page.width)):
        crop = page.crop((x0, top, x1, bottom))
        text = crop.extract_text(x_tolerance=1, y_tolerance=3) or ""
        if text.strip():
            parts.append(text)
    return "\n".join(parts)


def iter_year_segments(pdf, headings):
    by_page: dict[int, list[tuple[float, str]]] = {}
    for page_index, y, year in headings:
        by_page.setdefault(page_index, []).append((y, year))

    current_year = None
    for page_index, page in enumerate(pdf.pages):
        page_headings = sorted(by_page.get(page_index, []))
        start_y = 0.0

        for y, year in page_headings:
            if current_year and y > start_y + 20:
                yield current_year, page_index + 1, start_y, y, extract_band_text(page, start_y, y)
            current_year = year
            start_y = y + 18

        if current_year:
            yield current_year, page_index + 1, start_y, page.height, extract_band_text(page, start_y, page.height)


def iter_question_chunks(segment_text: str):
    current_num = None
    current_lines: list[str] = []

    for raw_line in segment_text.splitlines():
        line = clean_text(raw_line)
        if not line:
            continue
        if YEAR_RE.search(line):
            continue
        if re.match(r"^(?:mathemat|matics|tics)\s*(?:\d{4})?$", line, flags=re.IGNORECASE):
            continue

        match = match_question_start(line)
        if match:
            if current_num is not None and current_lines:
                yield current_num, clean_text("\n".join(current_lines))
            current_num, rest = match
            current_lines = [rest] if rest else []
        elif current_num is not None:
            current_lines.append(line)

    if current_num is not None and current_lines:
        yield current_num, clean_text("\n".join(current_lines))


def split_options(chunk: str):
    matches = list(OPTION_RE.finditer(chunk))
    if not matches:
        return chunk, {}

    question_text = clean_text(chunk[: matches[0].start()])
    options = {}
    for index, match in enumerate(matches):
        letter = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(chunk)
        options[letter] = clean_text(chunk[start:end])
    return question_text, options


def likely_needs_image_review(text: str) -> bool:
    lowered = text.lower()
    markers = (
        "figure above",
        "diagram above",
        "graph above",
        "pie chart",
        "bar chart",
        "table below",
        "figure below",
        "diagram below",
        "chart above",
    )
    return any(marker in lowered for marker in markers)


def build_rows(pdf_path: Path):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        headings = iter_heading_positions(pdf)
        seen = set()
        for year, page_number, _top, _bottom, text in iter_year_segments(pdf, headings):
            for question_number, chunk in iter_question_chunks(text):
                key = (year, question_number)
                if key in seen:
                    continue
                seen.add(key)

                question_text, options = split_options(chunk)
                if not question_text:
                    continue
                missing_required_options = [
                    letter for letter in ("A", "B", "C", "D") if not options.get(letter, "").strip()
                ]

                rows.append(
                    {
                        "question_id": f"MTH-{year}-{question_number:03d}",
                        "exam_type": "JAMB",
                        "subject": "Mathematics",
                        "topic": "Past Questions",
                        "subtopic": "",
                        "difficulty": "medium",
                        "year": year,
                        "passage_id": "",
                        "question_text": question_text,
                        "image_url": "",
                        "option_a": options.get("A", ""),
                        "option_b": options.get("B", ""),
                        "option_c": options.get("C", ""),
                        "option_d": options.get("D", ""),
                        "option_e": options.get("E", ""),
                        "correct_option": "",
                        "explanation": "",
                        "tags": f"mathematics|jamb|{year}|pdf|needs-answer",
                        "source": "past-question",
                        "status": "draft",
                        "source_pdf": str(pdf_path),
                        "source_page": page_number,
                        "pdf_question_number": question_number,
                        "needs_answer_key": "yes",
                        "needs_option_review": "yes" if missing_required_options else "no",
                        "needs_image_review": "yes" if likely_needs_image_review(chunk) else "no",
                    }
                )
    return rows


def write_csv(rows, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "question_id",
        "exam_type",
        "subject",
        "topic",
        "subtopic",
        "difficulty",
        "year",
        "passage_id",
        "question_text",
        "image_url",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "option_e",
        "correct_option",
        "explanation",
        "tags",
        "source",
        "status",
        "source_pdf",
        "source_page",
        "pdf_question_number",
        "needs_answer_key",
        "needs_option_review",
        "needs_image_review",
    ]
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Extract JAMB Mathematics PDF questions to a review CSV.")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = build_rows(args.pdf)
    write_csv(rows, args.out)

    counts: dict[str, int] = {}
    image_review_count = 0
    option_review_count = 0
    option_e_count = 0
    for row in rows:
        counts[row["year"]] = counts.get(row["year"], 0) + 1
        if row["needs_image_review"] == "yes":
            image_review_count += 1
        if row["needs_option_review"] == "yes":
            option_review_count += 1
        if row["option_e"]:
            option_e_count += 1

    print(f"Wrote {len(rows)} rows to {args.out}")
    print("Counts by year:")
    for year in sorted(counts):
        print(f"  {year}: {counts[year]}")
    print(f"Rows with option E: {option_e_count}")
    print(f"Rows needing option review: {option_review_count}")
    print(f"Rows needing image/diagram review: {image_review_count}")


if __name__ == "__main__":
    main()
