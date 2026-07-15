import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { AchievementsResponse } from '../api/types';
import Card from '../components/ui/Card';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';

export default function Achievements() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['achievements'],
    queryFn: () => api.get<AchievementsResponse>('/api/achievements'),
  });

  if (isLoading) return <Spinner className="w-8 h-8 mt-16" />;
  if (error || !data) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16">
        <EmptyState icon="fa-solid fa-triangle-exclamation" title="Couldn't load achievements" />
      </div>
    );
  }

  const earnedCount = data.items.filter((a) => a.earned).length;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6">
        <h1 className="font-display font-extrabold text-2xl text-ink-900">
          <i className="fa-solid fa-medal text-warning-500 mr-2" />
          Achievements
        </h1>
        <p className="text-ink-500 mt-1">
          {earnedCount} of {data.items.length} unlocked
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {data.items.map((a) => (
          <Card
            key={a.code}
            padding="lg"
            className={`flex flex-col items-center text-center gap-2 ${a.earned ? '' : 'opacity-50'}`}
          >
            <div
              className={`w-14 h-14 rounded-full flex items-center justify-center text-xl ${
                a.earned ? 'bg-warning-50 text-warning-500' : 'bg-ink-100 text-ink-400'
              }`}
            >
              <i className={a.earned ? a.icon : 'fa-solid fa-lock'} />
            </div>
            <p className="font-display font-bold text-sm text-ink-900">{a.title}</p>
            <p className="text-xs text-ink-500 leading-relaxed">{a.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
