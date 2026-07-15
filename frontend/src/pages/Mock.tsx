import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { api, ApiError } from '../api/client';
import type { QuizAttempt, Subject } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Skeleton from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';

const SUBJECT_ICONS: Record<string, string> = {
  Mathematics: 'fa-solid fa-square-root-variable',
  Physics: 'fa-solid fa-atom',
  Chemistry: 'fa-solid fa-flask',
  Biology: 'fa-solid fa-dna',
  Geography: 'fa-solid fa-earth-africa',
  Economics: 'fa-solid fa-chart-pie',
  Literature: 'fa-solid fa-book',
  Government: 'fa-solid fa-landmark',
  Commerce: 'fa-solid fa-handshake',
  Accounting: 'fa-solid fa-calculator',
};

const REQUIRED_COUNT = 3;

export default function Mock() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string[]>([]);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.get<Subject[]>('/api/subjects'),
  });

  const otherSubjects = (data ?? []).filter((s) => s.name !== 'English');

  const toggle = (name: string) => {
    setSelected((prev) => {
      if (prev.includes(name)) return prev.filter((s) => s !== name);
      if (prev.length >= REQUIRED_COUNT) return prev;
      return [...prev, name];
    });
  };

  const startMock = async () => {
    if (selected.length !== REQUIRED_COUNT || starting) return;
    setStarting(true);
    setError(null);
    try {
      const attempt = await api.post<QuizAttempt>('/api/mock/start', { subjects: selected });
      navigate(`/quiz-attempt/${attempt.attempt_id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not start the mock exam.');
      setStarting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6">
        <h1 className="font-display font-extrabold text-2xl text-ink-900">
          <i className="fa-solid fa-file-signature text-brand-600 mr-2" />
          Full JAMB Mock
        </h1>
        <p className="text-ink-500 mt-1">
          The real UTME format: English (compulsory) + 3 subjects of your choice — 180 questions, 120 minutes.
        </p>
      </div>

      {error && (
        <Card padding="sm" className="mb-4 bg-danger-50 border-danger-100 text-danger-600 text-sm font-semibold">
          {error}
        </Card>
      )}

      <Card padding="md" className="mb-6 bg-brand-50/40 border-brand-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-brand-500 text-white flex items-center justify-center text-sm flex-shrink-0">
            <i className="fa-solid fa-language" />
          </div>
          <div>
            <p className="font-display font-bold text-sm text-ink-900">English</p>
            <p className="text-xs text-ink-500">Compulsory — 60 questions, included automatically</p>
          </div>
        </div>
      </Card>

      {isLoading && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      )}

      {otherSubjects.length === 0 && !isLoading && (
        <EmptyState icon="fa-solid fa-file-signature" title="No subjects available" />
      )}

      {otherSubjects.length > 0 && (
        <>
          <p className="font-semibold text-ink-900 text-sm mb-3">
            Pick {REQUIRED_COUNT} more subjects ({selected.length}/{REQUIRED_COUNT} selected)
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
            {otherSubjects.map((s) => {
              const isSelected = selected.includes(s.name);
              const disabled = !isSelected && selected.length >= REQUIRED_COUNT;
              return (
                <button
                  key={s.name}
                  type="button"
                  onClick={() => toggle(s.name)}
                  disabled={disabled}
                  className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-left transition-colors ${
                    isSelected
                      ? 'border-brand-500 bg-brand-50'
                      : disabled
                      ? 'border-ink-100 opacity-40 cursor-not-allowed'
                      : 'border-ink-200 hover:border-brand-300 hover:bg-brand-50/50'
                  }`}
                >
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-sm flex-shrink-0 ${
                    isSelected ? 'bg-brand-500 text-white' : 'bg-brand-50 text-brand-600'
                  }`}>
                    <i className={SUBJECT_ICONS[s.name] ?? 'fa-solid fa-book-open'} />
                  </div>
                  <span className="font-display font-bold text-sm text-ink-900">{s.name}</span>
                  {isSelected && <i className="fa-solid fa-circle-check text-brand-500 ml-auto" />}
                </button>
              );
            })}
          </div>

          <Card padding="lg">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="text-sm text-ink-500">
                <span className="font-semibold text-ink-900">180 questions</span> · 120 minutes · one sitting
              </div>
              <Button size="lg" onClick={startMock} disabled={selected.length !== REQUIRED_COUNT || starting}>
                <i className="fa-solid fa-file-signature mr-2" />
                {starting ? 'Starting…' : 'Start Mock Exam'}
              </Button>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
