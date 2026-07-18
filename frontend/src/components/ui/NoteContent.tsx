import { useMemo } from 'react';
import MathText from './MathText';

/**
 * Renders a LessonNote's content_md, a small constrained syntax (not full
 * Markdown -- deliberately narrow so app/ai.py's generation prompt can
 * reliably produce it and this renderer can stay dependency-free):
 *   "## "     section heading
 *   "- "      bullet list item (consecutive lines group into one <ul>)
 *   "Example N: ..."  worked example -- gets a highlighted callout block
 *   "**text**" inline bold (works inside headings/bullets/paragraphs too)
 *   "\( ... \)" inline math, rendered via the same MathText/KaTeX path
 *               already used for question text elsewhere in the app.
 */

type Block =
  | { type: 'heading'; text: string }
  | { type: 'bullets'; items: string[] }
  | { type: 'example'; lines: string[] }
  | { type: 'paragraph'; lines: string[] };

const EXAMPLE_RE = /^Example\s+\d+\s*:/i;

function parseBlocks(md: string): Block[] {
  const rawLines = md.replace(/\r\n/g, '\n').split('\n');
  const blocks: Block[] = [];
  let i = 0;

  const isBreak = (s: string) => s.startsWith('## ') || s.startsWith('- ') || EXAMPLE_RE.test(s);

  while (i < rawLines.length) {
    const line = rawLines[i].trim();
    if (!line) {
      i++;
      continue;
    }
    if (line.startsWith('## ')) {
      blocks.push({ type: 'heading', text: line.slice(3).trim() });
      i++;
      continue;
    }
    if (line.startsWith('- ')) {
      const items: string[] = [];
      while (i < rawLines.length && rawLines[i].trim().startsWith('- ')) {
        items.push(rawLines[i].trim().slice(2).trim());
        i++;
      }
      blocks.push({ type: 'bullets', items });
      continue;
    }
    if (EXAMPLE_RE.test(line)) {
      // The opening "Example N:" line always matches isBreak (it's an
      // example line itself), so it must be consumed unconditionally here --
      // otherwise the loop below never advances past it and spins forever.
      const lines: string[] = [rawLines[i].trim()];
      i++;
      while (i < rawLines.length && rawLines[i].trim() && !isBreak(rawLines[i].trim())) {
        lines.push(rawLines[i].trim());
        i++;
      }
      blocks.push({ type: 'example', lines });
      continue;
    }
    const lines: string[] = [];
    while (i < rawLines.length && rawLines[i].trim() && !isBreak(rawLines[i].trim())) {
      lines.push(rawLines[i].trim());
      i++;
    }
    blocks.push({ type: 'paragraph', lines });
  }
  return blocks;
}

function parseInline(text: string): { bold: boolean; text: string }[] {
  const parts: { bold: boolean; text: string }[] = [];
  const regex = /\*\*(.+?)\*\*/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(text))) {
    if (match.index > lastIndex) parts.push({ bold: false, text: text.slice(lastIndex, match.index) });
    parts.push({ bold: true, text: match[1] });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) parts.push({ bold: false, text: text.slice(lastIndex) });
  return parts.length ? parts : [{ bold: false, text }];
}

function InlineText({ text }: { text: string }) {
  return (
    <>
      {parseInline(text).map((p, i) =>
        p.bold ? (
          <strong key={i} className="font-semibold text-ink-900">
            <MathText text={p.text} />
          </strong>
        ) : (
          <MathText key={i} text={p.text} />
        )
      )}
    </>
  );
}

export default function NoteContent({ content }: { content: string }) {
  const blocks = useMemo(() => parseBlocks(content), [content]);

  return (
    <div className="space-y-4">
      {blocks.map((b, i) => {
        if (b.type === 'heading') {
          return (
            <h2 key={i} className="font-display font-bold text-lg text-ink-900 mt-2 first:mt-0">
              {b.text}
            </h2>
          );
        }
        if (b.type === 'bullets') {
          return (
            <ul key={i} className="list-disc list-outside pl-5 space-y-1.5 text-ink-700 leading-relaxed">
              {b.items.map((item, j) => (
                <li key={j}>
                  <InlineText text={item} />
                </li>
              ))}
            </ul>
          );
        }
        if (b.type === 'example') {
          return (
            <div key={i} className="bg-brand-50 border border-brand-100 rounded-xl p-4 space-y-1.5">
              {b.lines.map((line, j) => (
                <p key={j} className={j === 0 ? 'font-semibold text-brand-700 text-sm' : 'text-ink-700 text-sm leading-relaxed'}>
                  <InlineText text={line} />
                </p>
              ))}
            </div>
          );
        }
        return (
          <div key={i} className="space-y-1.5 text-ink-700 leading-relaxed">
            {b.lines.map((line, j) => (
              <p key={j}>
                <InlineText text={line} />
              </p>
            ))}
          </div>
        );
      })}
    </div>
  );
}
