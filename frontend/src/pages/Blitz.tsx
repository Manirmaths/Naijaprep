import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { api, ApiError } from '../api/client';
import type { QuizAttempt, Subject } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Select } from '../components/ui/Input';
import Skeleton from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';

const SUBJECT_ICONS: Record<string, string> = {
  Mathematics: 'fa-solid fa-square-root-variable',
  English: 'fa-solid fa-language',
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

export default function Blitz() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string | null>(null);
  const [difficulty, setDifficulty] = useState('any');
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.get<Subject[]>('/api/subjects'),
  });

  const startBlitz = async () => {
    if (!selected || starting) return;
    setStarting(true);
    setError(null);
    try {
      const attempt = await api.post<QuizAttempt>('/api/blitz/start', {
        subject: selected,
        difficulty: difficulty !== 'any' ? difficulty : null,
      });
      navigate(`/quiz-attempt/${attempt.attempt_id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not start Blitz round.');
      setStarting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6">
        <h1 className="font-display font-extrabold text-2xl text-ink-900">
          <i className="fa-solid fa-bolt text-flame-500 mr-2" />
          Blitz Challenge
        </h1>
        <p className="text-ink-500 mt-1">
          Pick a subject and race the clock — 3 minutes, as many questions as you can get right.
        </p>
      </div>

      {error && (
        <Card padding="sm" className="mb-4 bg-danger-50 border-danger-100 text-danger-600 text-sm font-semibold">
          {error}
        </Card>
      )}

      {isLoading && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      )}

      {data && data.length === 0 && (
        <EmptyState icon="fa-solid fa-bolt" title="No subjects available" />
      )}

      {data && data.length > 0 && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
            {data.map((s) => {
              const isSelected = selected === s.name;
              return (
                <button
                  key={s.name}
                  type="button"
                  onClick={() => setSelected(s.name)}
                  className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-left transition-colors ${
                    isSelected ? 'border-brand-500 bg-brand-50' : 'border-ink-200 hover:border-brand-300 hover:bg-brand-50/50'
                  }`}
                >
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-sm flex-shrink-0 ${
                    isSelected ? 'bg-brand-500 text-white' : 'bg-brand-50 text-brand-600'
                  }`}>
                    <i className={SUBJECT_ICONS[s.name] ?? 'fa-solid fa-book-open'} />
                  </div>
                  <span className="font-display font-bold text-sm text-ink-900">{s.name}</span>
                </button>
              );
            })}
          </div>

          <Card padding="lg">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="font-semibold text-ink-900 text-sm mb-1">Difficulty</p>
                <Select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="!w-auto">
                  <option value="any">Any level</option>
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </Select>
              </div>
              <Button size="lg" onClick={startBlitz} disabled={!selected || starting}>
                <i className="fa-solid fa-bolt mr-2" />
                {starting ? 'Starting…' : 'Start Blitz'}
              </Button>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
