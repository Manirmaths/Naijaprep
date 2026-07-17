import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { LearnHub as LearnHubData } from '../api/types';
import Card from '../components/ui/Card';
import ProgressBar from '../components/ui/ProgressBar';
import Spinner from '../components/ui/Spinner';
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

export default function LearnHub() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['learn-hub'],
    queryFn: () => api.get<LearnHubData>('/api/notes/learn-hub'),
  });

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6">
        <h1 className="font-display font-extrabold text-2xl text-ink-900">
          <i className="fa-solid fa-graduation-cap text-brand-500 mr-2" />
          Learn
        </h1>
        <p className="text-ink-500 mt-1">Read lesson notes topic by topic, then jump straight into practice.</p>
      </div>

      {isLoading && <Spinner className="w-8 h-8 mt-8" />}
      {error && <EmptyState icon="fa-solid fa-triangle-exclamation" title="Couldn't load your progress" />}

      {data && (
        <div className="space-y-3">
          {data.subjects.map((s) => (
            <Link key={s.subject} to={`/subjects/${encodeURIComponent(s.subject)}`}>
              <Card padding="md" interactive className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center text-base flex-shrink-0">
                  <i className={SUBJECT_ICONS[s.subject] ?? 'fa-solid fa-book-open'} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-display font-bold text-ink-900">{s.subject}</span>
                    <span className="text-xs font-semibold text-ink-400">
                      {s.read_topics}/{s.total_topics} read
                    </span>
                  </div>
                  <ProgressBar value={s.percentage} tone={s.percentage >= 70 ? 'success' : s.percentage >= 40 ? 'warning' : 'danger'} />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
