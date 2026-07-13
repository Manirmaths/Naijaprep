import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import type { Dashboard as DashboardData } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import ProgressBar from '../components/ui/ProgressBar';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';

function StatCard({ icon, label, value, tone }: { icon: string; label: string; value: string | number; tone: string }) {
  return (
    <Card padding="md" className="flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-lg flex-shrink-0 ${tone}`}>
        <i className={icon} />
      </div>
      <div>
        <p className="font-display font-extrabold text-2xl text-ink-900 leading-none">{value}</p>
        <p className="text-xs text-ink-500 mt-1 font-medium">{label}</p>
      </div>
    </Card>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get<DashboardData>('/api/dashboard'),
  });

  if (isLoading) return <Spinner className="w-8 h-8 mt-16" />;
  if (error || !data) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16">
        <EmptyState icon="fa-solid fa-triangle-exclamation" title="Couldn't load your dashboard" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="font-display font-extrabold text-2xl text-ink-900 mb-1">Welcome back, {user?.username}</h1>
      <p className="text-ink-500 mb-6">Here's how your practice is going.</p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard icon="fa-solid fa-star" label="Total points" value={data.points} tone="bg-brand-50 text-brand-600" />
        <StatCard icon="fa-solid fa-fire" label="Current streak" value={`${data.current_streak}d`} tone="bg-flame-500/10 text-flame-500" />
        <StatCard icon="fa-solid fa-trophy" label="Longest streak" value={`${data.longest_streak}d`} tone="bg-warning-50 text-warning-600" />
        <StatCard icon="fa-solid fa-bookmark" label="Marked questions" value={data.review_count} tone="bg-info-50 text-info-500" />
      </div>

      {!data.has_taken_diagnostic && (
        <Card padding="md" className="bg-brand-50 border-brand-100 mb-6 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-brand-800 font-medium">
            <i className="fa-solid fa-circle-info mr-1.5" />
            New here? Start with any subject to build your first topic stats.
          </p>
          <Link to="/subjects">
            <Button size="sm">Start practicing</Button>
          </Link>
        </Card>
      )}

      <Card padding="lg">
        <h2 className="font-display font-bold text-lg text-ink-900 mb-4">Topic performance</h2>
        {data.topic_stats.length > 0 ? (
          <div className="space-y-4">
            {data.topic_stats.map((t) => (
              <div key={t.topic}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-semibold text-ink-700">{t.topic}</span>
                  <span className="text-ink-400 text-xs font-medium">
                    {t.correct}/{t.total} ({t.percentage}%)
                  </span>
                </div>
                <ProgressBar value={t.percentage} tone={t.percentage >= 70 ? 'success' : t.percentage >= 40 ? 'warning' : 'danger'} />
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon="fa-solid fa-chart-line"
            title="No practice data yet"
            description="Take a quiz to start tracking your accuracy by topic."
            action={
              <Link to="/subjects">
                <Button size="sm">Practice now</Button>
              </Link>
            }
          />
        )}
      </Card>

      <div className="flex flex-wrap items-center justify-between gap-3 mt-6">
        <Link to="/subjects">
          <Button icon={<i className="fa-solid fa-play" />}>Practice more</Button>
        </Link>
        <Link to="/review" className="text-sm font-semibold text-brand-600 hover:text-brand-700">
          View marked questions <i className="fa-solid fa-arrow-right ml-1" />
        </Link>
      </div>
    </div>
  );
}
