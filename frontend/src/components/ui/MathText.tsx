import { Fragment, useMemo } from 'react';
import katex from 'katex';

/**
 * Renders text that may contain inline LaTeX math wrapped in \( ... \)
 * (and, for completeness, $$ ... $$ as a block-math fallback).
 * Plain text renders as-is; math segments render through KaTeX.
 */
export default function MathText({ text, className }: { text?: string | null; className?: string }) {
  const parts = useMemo(() => splitMath(text || ''), [text]);

  if (parts.length === 1 && parts[0].type === 'text') {
    return <span className={className}>{parts[0].value}</span>;
  }

  return (
    <span className={className}>
      {parts.map((part, i) => {
        if (part.type === 'text') return <Fragment key={i}>{part.value}</Fragment>;
        const html = renderKatex(part.value, part.display);
        return <span key={i} dangerouslySetInnerHTML={{ __html: html }} />;
      })}
    </span>
  );
}

type Part = { type: 'text'; value: string } | { type: 'math'; value: string; display: boolean };

function splitMath(input: string): Part[] {
  const parts: Part[] = [];
  // Matches \( ... \) for inline math and \[ ... \] for display math.
  const regex = /\\\((.+?)\\\)|\\\[(.+?)\\\]/gs;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(input)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: input.slice(lastIndex, match.index) });
    }
    if (match[1] !== undefined) {
      parts.push({ type: 'math', value: match[1], display: false });
    } else if (match[2] !== undefined) {
      parts.push({ type: 'math', value: match[2], display: true });
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < input.length) {
    parts.push({ type: 'text', value: input.slice(lastIndex) });
  }

  return parts.length ? parts : [{ type: 'text', value: input }];
}

function renderKatex(latex: string, display: boolean): string {
  try {
    return katex.renderToString(latex, { throwOnError: false, displayMode: display, output: 'html' });
  } catch {
    return latex;
  }
}
