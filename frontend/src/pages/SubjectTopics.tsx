import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { useState } from 'react';
import { api } from '../api/client';
import type { Topic } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Select } from '../components/ui/Input';
import Skeleton from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import { useAuth } from '../context/AuthContext';

export default function SubjectTopics() {
  const { subject = '' } = useParams();
  const { user } = useAuth();
  const [year, setYear] = useState('any');

  const { data, isLoading, error } = useQuery({
    queryKey: ['topics', subject],
    queryFn: () => api.get<Topic[]>(`/api/subjects/${encodeURIComponent(subject)}/topics`),
  });

  const { data: years } = useQuery({
    queryKey: ['years', subject],
    queryFn: () => api.get<string[]>(`/api/subjects/${encodeURIComponent(subject)}/years`),
  });

  const yearSuffix = year !== 'any' ? `&year=${encodeURIComponent(year)}` : '';

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <nav className="text-sm text-ink-400 mb-3">
        <Link to="/subjects" className="hover:text-brand-600">Subjects</Link>
        <span className="mx-1.5">/</span>
        <span className="text-ink-600 font-medium">{subject}</span>
      </nav>

      <div className="flex flex-wrap justify-between items-center gap-3 mb-4">
        <h1 className="font-display font-extrabold text-2xl text-ink-900">{subject}</h1>
        <div className="flex gap-2">
          <Link to="/subjects">
            <Button variant="outline" size="sm">Back</Button>
          </Link>
          <Link to={`/quiz?subject=${encodeURIComponent(subject)}${yearSuffix}`}>
            <Button size="sm">Quick 5-question quiz</Button>
          </Link>
        </div>
      </div>

      {years && years.length > 0 && (
        <div className="flex items-center gap-2 mb-6">
          <label className="text-sm font-medium text-ink-500 flex items-center gap-1.5">
            <i className="fa-regular fa-calendar" /> Exam year
          </label>
          <Select value={year} onChange={(e) => setYear(e.target.value)} className="!w-auto !py-1.5 !px-2 !text-sm">
            <option value="any">All years</option>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </Select>
          {year !== 'any' && (
            <span className="text-xs text-ink-400">Only {year} past questions will be used</span>
          )}
        </div>
      )}

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-14" />
          ))}
        </div>
      )}

      {error && <EmptyState icon="fa-solid fa-triangle-exclamation" title="Couldn't load topics" description="Please refresh the page to try again." />}

      {data && data.length === 0 && (
        <EmptyState icon="fa-solid fa-book-open" title="No topics yet" description="Questions for this subject haven't been added yet." />
      )}

      <div className="space-y-2">
        {data?.map((t) => (
          <Card key={t.name} padding="sm" interactive className="flex items-center justify-between">
            <Link
              to={`/quiz?subject=${encodeURIComponent(subject)}&topic=${encodeURIComponent(t.name)}${yearSuffix}`}
              className="font-semibold text-ink-800 hover:text-brand-600 flex-1"
            >
              {t.name}
            </Link>
            {user?.is_admin && (
              <span className="text-xs font-semibold bg-ink-100 text-ink-500 rounded-full px-2.5 py-1">{t.count} questions</span>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
