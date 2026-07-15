import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { api } from '../api/client';
import type { Subject } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Select } from '../components/ui/Input';
import Skeleton from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import { useAuth } from '../context/AuthContext';

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

export default function Subjects() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.get<Subject[]>('/api/subjects'),
  });

  const [choices, setChoices] = useState<Record<string, { n: string; difficulty: string }>>({});

  const getChoice = (name: string) => choices[name] || { n: '5', difficulty: 'any' };
  const setChoice = (name: string, patch: Partial<{ n: string; difficulty: string }>) =>
    setChoices((c) => ({ ...c, [name]: { ...getChoice(name), ...patch } }));

  const startQuiz = (name: string) => {
    const { n, difficulty } = getChoice(name);
    const params = new URLSearchParams({ subject: name, n });
    if (difficulty !== 'any') params.set('difficulty', difficulty);
    navigate(`/quiz?${params.toString()}`);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6">
        <h1 className="font-display font-extrabold text-2xl text-ink-900">Choose a subject</h1>
        <p className="text-ink-500 mt-1">Tap a subject to browse topics, or start a quick quiz right away.</p>
      </div>

      {isLoading && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      )}

      {error && <EmptyState icon="fa-solid fa-triangle-exclamation" title="Couldn't load subjects" description="Please refresh the page to try again." />}

      {data && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {data.map((s) => {
            const choice = getChoice(s.name);
            return (
              <Card key={s.name} padding="sm" className="flex flex-col">
                <Link to={`/subjects/${encodeURIComponent(s.name)}`} className="mb-4 group">
                  <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center text-base mb-3">
                    <i className={SUBJECT_ICONS[s.name] ?? 'fa-solid fa-book-open'} />
                  </div>
                  <div className="font-display font-bold text-ink-900 group-hover:text-brand-600 transition-colors">{s.name}</div>
                  {user?.is_admin ? (
                    <span className="inline-block mt-1.5 text-xs font-semibold text-ink-400">
                      {s.question_count} question{s.question_count === 1 ? '' : 's'}
                    </span>
                  ) : (
                    <span className="inline-block mt-1.5 text-xs font-semibold text-ink-400">
                      Tap to practice
                    </span>
                  )}
                </Link>
                <div className="mt-auto space-y-2">
                  <div className="flex gap-1.5">
                    <Select value={choice.n} onChange={(e) => setChoice(s.name, { n: e.target.value })} className="!py-1.5 !px-2 !text-xs">
                      <option value="5">5 Qs</option>
                      <option value="10">10 Qs</option>
                      <option value="20">20 Qs</option>
                    </Select>
                    <Select value={choice.difficulty} onChange={(e) => setChoice(s.name, { difficulty: e.target.value })} className="!py-1.5 !px-2 !text-xs">
                      <option value="any">Any level</option>
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </Select>
                  </div>
                  <Button size="sm" fullWidth onClick={() => startQuiz(s.name)} disabled={s.question_count === 0}>
                    Start quiz
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
