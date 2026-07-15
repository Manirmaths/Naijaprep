import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import type { Dashboard as DashboardData } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import ProgressBar from '../components/ui/ProgressBar';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';

const GOAL_PRESETS = [
  { value: 20, label: 'Casual' },
  { value: 50, label: 'Regular' },
  { value: 100, label: 'Serious' },
  { value: 150, label: 'Intense' },
];

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

function DailyGoalRing({ pointsToday, dailyGoal, goalMet }: { pointsToday: number; dailyGoal: number; goalMet: boolean }) {
  const size = 88;
  const stroke = 8;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(1, dailyGoal > 0 ? pointsToday / dailyGoal : 0));
  const offset = circumference * (1 - pct);

  return (
    <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="currentColor" strokeWidth={stroke} className="text-ink-100" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={goalMet ? 'text-success-500 transition-all duration-500' : 'text-brand-500 transition-all duration-500'}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        {goalMet ? (
          <i className="fa-solid fa-check text-success-500 text-xl" />
        ) : (
          <span className="font-display font-extrabold text-sm text-ink-900">{Math.round(pct * 100)}%</span>
        )}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user, refresh } = useAuth();
  const queryClient = useQueryClient();
  const [savingGoal, setSavingGoal] = useState(false);
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get<DashboardData>('/api/dashboard'),
  });

  const setGoal = async (value: number) => {
    if (savingGoal || value === data?.daily_goal) return;
    setSavingGoal(true);
    try {
      await api.put('/api/dashboard/daily-goal', { daily_goal: value });
      await Promise.all([queryClient.invalidateQueries({ queryKey: ['dashboard'] }), refresh()]);
    } finally {
      setSavingGoal(false);
    }
  };

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

      <Card padding="lg" className="mb-6 flex flex-wrap items-center gap-5">
        <DailyGoalRing pointsToday={data.points_today} dailyGoal={data.daily_goal} goalMet={data.goal_met} />
        <div className="flex-1 min-w-[180px]">
          <p className="font-display font-bold text-ink-900">
            {data.goal_met ? (
              <>Daily goal reached! <i className="fa-solid fa-champagne-glasses text-warning-500" /></>
            ) : (
              'Daily goal'
            )}
          </p>
          <p className="text-sm text-ink-500 mb-3">
            {data.points_today} / {data.daily_goal} XP today
          </p>
          <div className="flex flex-wrap gap-1.5">
            {GOAL_PRESETS.map((p) => (
              <button
                key={p.value}
                onClick={() => setGoal(p.value)}
                disabled={savingGoal}
                className={`text-xs font-semibold rounded-full px-3 py-1.5 transition-colors ${
                  data.daily_goal === p.value
                    ? 'bg-brand-500 text-white'
                    : 'bg-ink-100 text-ink-600 hover:bg-ink-200'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </Card>

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
        <div className="flex items-center gap-4">
          <Link to="/achievements" className="text-sm font-semibold text-brand-600 hover:text-brand-700">
            <i className="fa-solid fa-medal mr-1" /> Achievements
          </Link>
          <Link to="/review" className="text-sm font-semibold text-brand-600 hover:text-brand-700">
            View marked questions <i className="fa-solid fa-arrow-right ml-1" />
          </Link>
        </div>
      </div>
    </div>
  );
}
