import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { api, ApiError } from '../api/client';
import type { StudyPlan, Subject } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import Spinner from '../components/ui/Spinner';

const MAX_SUBJECTS = 4;

function fmtDay(dateStr: string) {
  const d = new Date(`${dateStr}T00:00:00`);
  return d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
}

export default function StudyPlanner() {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [examDate, setExamDate] = useState('');
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: plan, isLoading: planLoading } = useQuery({
    queryKey: ['study-plan'],
    queryFn: () => api.get<StudyPlan>('/api/study-planner'),
  });

  const { data: subjects } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.get<Subject[]>('/api/subjects'),
    enabled: editing || (plan !== undefined && !plan.configured),
  });

  useEffect(() => {
    if (plan && plan.configured) {
      setExamDate(plan.exam_date ?? '');
      setSelectedSubjects(plan.subjects);
    }
  }, [plan]);

  const toggleSubject = (name: string) => {
    setSelectedSubjects((prev) => {
      if (prev.includes(name)) return prev.filter((s) => s !== name);
      if (prev.length >= MAX_SUBJECTS) return prev;
      return [...prev, name];
    });
  };

  const savePlan = async () => {
    if (selectedSubjects.length === 0 || saving) return;
    setSaving(true);
    setError(null);
    try {
      await api.put('/api/study-planner', {
        exam_date: examDate || null,
        subjects: selectedSubjects,
      });
      await queryClient.invalidateQueries({ queryKey: ['study-plan'] });
      setEditing(false);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not save your study plan.');
    } finally {
      setSaving(false);
    }
  };

  if (planLoading) return <Spinner className="w-8 h-8 mt-16" />;

  const showSetupForm = editing || !plan?.configured;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="font-display font-extrabold text-2xl text-ink-900">
            <i className="fa-solid fa-calendar-days text-brand-500 mr-2" />
            Study Planner
          </h1>
          <p className="text-ink-500 mt-1">
            A day-by-day plan built from your weakest topics, refreshed automatically every time you check it.
          </p>
        </div>
        {plan?.configured && !editing && (
          <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
            <i className="fa-solid fa-pen mr-1.5" /> Edit
          </Button>
        )}
      </div>

      {error && (
        <Card padding="sm" className="mb-4 bg-danger-50 border-danger-100 text-danger-600 text-sm font-semibold">
          {error}
        </Card>
      )}

      {showSetupForm && (
        <Card padding="lg" className="mb-6">
          <h2 className="font-display font-bold text-ink-900 mb-4">
            {plan?.configured ? 'Update your plan' : 'Set up your plan'}
          </h2>

          <Input
            type="date"
            label="Exam date (optional)"
            hint="If you know when you're sitting the exam, we'll count down to it."
            value={examDate}
            min={new Date().toISOString().slice(0, 10)}
            onChange={(e) => setExamDate(e.target.value)}
            className="max-w-xs mb-5"
          />

          <p className="text-sm font-semibold text-ink-800 mb-2">
            Subjects to rotate through <span className="text-ink-400 font-normal">(up to {MAX_SUBJECTS})</span>
          </p>
          {!subjects ? (
            <Spinner className="w-6 h-6" />
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-6">
              {subjects.map((s) => {
                const isSelected = selectedSubjects.includes(s.name);
                return (
                  <button
                    key={s.name}
                    type="button"
                    onClick={() => toggleSubject(s.name)}
                    disabled={!isSelected && selectedSubjects.length >= MAX_SUBJECTS}
                    className={`rounded-xl border px-3 py-2.5 text-left text-sm font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
                      isSelected ? 'border-brand-500 bg-brand-50 text-brand-700' : 'border-ink-200 text-ink-700 hover:border-brand-300'
                    }`}
                  >
                    {s.name}
                  </button>
                );
              })}
            </div>
          )}

          <div className="flex items-center gap-3">
            <Button onClick={savePlan} disabled={selectedSubjects.length === 0 || saving}>
              {saving ? 'Saving…' : 'Save plan'}
            </Button>
            {plan?.configured && (
              <Button variant="ghost" onClick={() => setEditing(false)} disabled={saving}>
                Cancel
              </Button>
            )}
          </div>
        </Card>
      )}

      {plan?.configured && !editing && plan.today && (
        <>
          <Card padding="lg" className="mb-6 bg-brand-50 border-brand-100">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs font-bold text-brand-600 uppercase tracking-wide mb-1">Today's focus</p>
                <h2 className="font-display font-extrabold text-xl text-ink-900">{plan.today.subject}</h2>
                {plan.today.topic && <p className="text-sm text-ink-600 mt-1">Weakest topic: {plan.today.topic}</p>}
                {plan.days_until_exam !== null && (
                  <p className="text-xs text-ink-500 mt-2">
                    <i className="fa-solid fa-hourglass-half mr-1" />
                    {plan.days_until_exam >= 0 ? `${plan.days_until_exam} day${plan.days_until_exam === 1 ? '' : 's'} until your exam` : 'Exam date has passed'}
                  </p>
                )}
              </div>
              <Link
                to={`/quiz?subject=${encodeURIComponent(plan.today.subject)}${plan.today.topic ? `&topic=${encodeURIComponent(plan.today.topic)}` : ''}&n=${plan.today.question_count}`}
              >
                <Button size="lg" icon={<i className="fa-solid fa-play" />}>
                  Start today's practice
                </Button>
              </Link>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="font-display font-bold text-sm text-ink-900 mb-4">
              <i className="fa-solid fa-calendar-week text-brand-500 mr-1.5" />
              This week
            </h2>
            <div className="space-y-2">
              {plan.week.map((task, i) => (
                <Link
                  key={task.date}
                  to={`/quiz?subject=${encodeURIComponent(task.subject)}${task.topic ? `&topic=${encodeURIComponent(task.topic)}` : ''}&n=${task.question_count}`}
                  className={`flex items-center justify-between rounded-xl px-3.5 py-2.5 -mx-1 transition-colors hover:bg-ink-50 ${i === 0 ? 'bg-ink-50' : ''}`}
                >
                  <div>
                    <p className="text-xs font-semibold text-ink-400">{fmtDay(task.date)}</p>
                    <p className="text-sm font-semibold text-ink-800">
                      {task.subject}
                      {task.topic && <span className="text-ink-400 font-normal"> · {task.topic}</span>}
                    </p>
                  </div>
                  <i className="fa-solid fa-chevron-right text-ink-300 text-xs" />
                </Link>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
