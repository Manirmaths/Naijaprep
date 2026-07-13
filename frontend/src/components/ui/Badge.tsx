import type { ReactNode } from 'react';
import type { Difficulty, QuestionStatus } from '../../api/types';

type Tone = 'brand' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';

const toneClasses: Record<Tone, string> = {
  brand: 'bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200',
  success: 'bg-success-50 text-success-600 ring-1 ring-inset ring-success-500/20',
  warning: 'bg-warning-50 text-warning-600 ring-1 ring-inset ring-warning-500/20',
  danger: 'bg-danger-50 text-danger-600 ring-1 ring-inset ring-danger-500/20',
  info: 'bg-info-50 text-info-500 ring-1 ring-inset ring-info-500/20',
  neutral: 'bg-ink-100 text-ink-600 ring-1 ring-inset ring-ink-200',
};

export default function Badge({ tone = 'neutral', children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${toneClasses[tone]}`}>
      {children}
    </span>
  );
}

const difficultyTone: Record<Difficulty, Tone> = {
  easy: 'success',
  medium: 'warning',
  hard: 'danger',
};

export function DifficultyBadge({ difficulty }: { difficulty: Difficulty }) {
  return <Badge tone={difficultyTone[difficulty] ?? 'neutral'}>{difficulty}</Badge>;
}

export function StatusBadge({ status }: { status: QuestionStatus }) {
  return <Badge tone={status === 'active' ? 'success' : 'neutral'}>{status}</Badge>;
}
