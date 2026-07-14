import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { api, ApiError } from '../api/client';
import { useAuth } from '../context/AuthContext';
import type { AdminQuestion, AdminStats, AdminUser, Difficulty, Passage, QuestionSource, QuestionStatus } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Avatar from '../components/ui/Avatar';
import { Input, Select, Textarea } from '../components/ui/Input';
import { DifficultyBadge, StatusBadge } from '../components/ui/Badge';
import Skeleton from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';

interface FormState {
  question_id: string;
  subject: string;
  topic: string;
  subtopic: string;
  difficulty: Difficulty;
  exam_type: string;
  year: string;
  passage_id: string;
  question_text: string;
  image_url: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_option: string;
  explanation: string;
  tags: string;
  source: QuestionSource;
  status: QuestionStatus;
}

const emptyForm: FormState = {
  question_id: '', subject: '', topic: '', subtopic: '', difficulty: 'medium',
  exam_type: '', year: '', passage_id: '',
  question_text: '', image_url: '', option_a: '', option_b: '', option_c: '', option_d: '',
  correct_option: 'A', explanation: '', tags: '', source: 'original', status: 'active',
};

function StatBlock({ value, label }: { value: number | string; label: string }) {
  return (
    <Card padding="md" className="text-center">
      <div className="font-display font-extrabold text-2xl text-ink-900">{value}</div>
      <div className="text-xs text-ink-500 mt-1 font-medium">{label}</div>
    </Card>
  );
}

export default function Admin() {
  const { user: me } = useAuth();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<'questions' | 'users'>('questions');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [editing, setEditing] = useState<AdminQuestion | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userError, setUserError] = useState<string | null>(null);

  const { data: stats } = useQuery({ queryKey: ['admin-stats'], queryFn: () => api.get<AdminStats>('/api/admin/stats') });
  const { data: passages } = useQuery({ queryKey: ['admin-passages'], queryFn: () => api.get<Passage[]>('/api/admin/passages') });
  const { data: questions, isLoading } = useQuery({
    queryKey: ['admin-questions', subjectFilter],
    queryFn: () => api.get<AdminQuestion[]>(`/api/admin/questions${subjectFilter ? `?subject=${encodeURIComponent(subjectFilter)}` : ''}`),
    enabled: tab === 'questions',
  });
  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => api.get<AdminUser[]>('/api/admin/users'),
    enabled: tab === 'users',
  });

  const openNew = () => { setEditing(null); setForm(emptyForm); setShowForm(true); setError(null); };
  const openEdit = (q: AdminQuestion) => {
    setEditing(q);
    setForm({
      question_id: q.question_id, subject: q.subject, topic: q.topic, subtopic: q.subtopic || '',
      difficulty: q.difficulty, exam_type: q.exam_type || '', year: q.year || '', passage_id: q.passage_id || '',
      question_text: q.question_text, image_url: q.image_url || '',
      option_a: q.option_a, option_b: q.option_b, option_c: q.option_c, option_d: q.option_d,
      correct_option: q.correct_option, explanation: q.explanation || '',
      tags: q.tags || '', source: q.source, status: q.status,
    });
    setShowForm(true);
    setError(null);
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    const payload = { ...form, passage_id: form.passage_id || null };
    try {
      if (editing) {
        await api.put(`/api/admin/questions/${editing.id}`, payload);
      } else {
        await api.post('/api/admin/questions', payload);
      }
      setShowForm(false);
      queryClient.invalidateQueries({ queryKey: ['admin-questions'] });
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    }
  };

  const remove = async (id: number) => {
    if (!confirm('Delete this question?')) return;
    await api.delete(`/api/admin/questions/${id}`);
    queryClient.invalidateQueries({ queryKey: ['admin-questions'] });
    queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
  };

  const removeUser = async (u: AdminUser) => {
    setUserError(null);
    if (!confirm(`Delete user "${u.username}"? This also removes their quiz history and cannot be undone.`)) return;
    try {
      await api.delete(`/api/admin/users/${u.id}`);
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
    } catch (err) {
      setUserError(err instanceof ApiError ? err.message : 'Something went wrong.');
    }
  };

  const toggleAdmin = async (u: AdminUser) => {
    setUserError(null);
    const verb = u.is_admin ? 'remove admin from' : 'make admin';
    if (!confirm(`Are you sure you want to ${verb} "${u.username}"?`)) return;
    try {
      await api.post(`/api/admin/users/${u.id}/toggle-admin`);
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    } catch (err) {
      setUserError(err instanceof ApiError ? err.message : 'Something went wrong.');
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex flex-wrap justify-between items-center gap-3 mb-6">
        <div>
          <h1 className="font-display font-extrabold text-2xl text-ink-900">Admin</h1>
          <p className="text-ink-500 text-sm mt-0.5">Manage questions and users.</p>
        </div>
        {tab === 'questions' && (
          <Button onClick={openNew} icon={<i className="fa-solid fa-plus" />}>Add question</Button>
        )}
      </div>

      {stats && (
        <div className="grid grid-cols-3 gap-3 mb-6">
          <StatBlock value={stats.total_questions} label="Total questions" />
          <StatBlock value={stats.total_users} label="Total users" />
          <StatBlock value={passages?.length ?? 0} label="Passages" />
        </div>
      )}

      <div className="flex gap-1 mb-6 border-b border-ink-100">
        <button
          onClick={() => setTab('questions')}
          className={`px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition-colors ${
            tab === 'questions' ? 'border-brand-500 text-brand-700' : 'border-transparent text-ink-500 hover:text-ink-800'
          }`}
        >
          <i className="fa-solid fa-book-open mr-1.5" /> Questions
        </button>
        <button
          onClick={() => setTab('users')}
          className={`px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition-colors ${
            tab === 'users' ? 'border-brand-500 text-brand-700' : 'border-transparent text-ink-500 hover:text-ink-800'
          }`}
        >
          <i className="fa-solid fa-users mr-1.5" /> Users
        </button>
      </div>

      {tab === 'users' ? (
        <>
          {userError && (
            <div className="bg-danger-50 text-danger-600 text-sm rounded-xl px-4 py-3 mb-4 flex items-center gap-2">
              <i className="fa-solid fa-circle-exclamation" /> {userError}
            </div>
          )}

          {usersLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
            </div>
          ) : users && users.length === 0 ? (
            <EmptyState icon="fa-solid fa-users" title="No users yet" />
          ) : (
            <Card padding="none" className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-ink-900 text-white">
                  <tr>
                    <th className="p-3 text-left font-semibold">User</th>
                    <th className="p-3 text-left font-semibold">Points</th>
                    <th className="p-3 text-left font-semibold">Streak</th>
                    <th className="p-3 text-left font-semibold">Role</th>
                    <th className="p-3 text-left font-semibold">Joined</th>
                    <th className="p-3 text-left font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users?.map((u) => (
                    <tr key={u.id} className="border-t border-ink-100 hover:bg-ink-50/60">
                      <td className="p-3">
                        <div className="flex items-center gap-3">
                          <Avatar name={u.username} size={32} />
                          <div>
                            <div className="font-semibold text-ink-800">
                              {u.username}
                              {me?.id === u.id && <span className="ml-1.5 text-xs font-medium text-ink-400">(you)</span>}
                            </div>
                            <div className="text-xs text-ink-400">{u.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="p-3 font-semibold text-ink-800">{u.points}</td>
                      <td className="p-3 text-ink-600">
                        <i className="fa-solid fa-fire text-flame-500 mr-1" />
                        {u.current_streak}d
                      </td>
                      <td className="p-3">
                        {u.is_admin ? <StatusBadge status="active" /> : <span className="text-ink-400 text-xs">Student</span>}
                      </td>
                      <td className="p-3 text-ink-500 text-xs">{new Date(u.created_at).toLocaleDateString()}</td>
                      <td className="p-3 whitespace-nowrap">
                        <button
                          onClick={() => toggleAdmin(u)}
                          disabled={me?.id === u.id}
                          className="text-brand-600 font-semibold mr-3 hover:underline disabled:text-ink-300 disabled:no-underline disabled:cursor-not-allowed"
                        >
                          {u.is_admin ? 'Remove admin' : 'Make admin'}
                        </button>
                        <button
                          onClick={() => removeUser(u)}
                          disabled={me?.id === u.id}
                          className="text-danger-500 font-semibold hover:underline disabled:text-ink-300 disabled:no-underline disabled:cursor-not-allowed"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )}
        </>
      ) : (
        <>
      <div className="mb-4 max-w-xs">
        <Select value={subjectFilter} onChange={(e) => setSubjectFilter(e.target.value)}>
          <option value="">All subjects</option>
          {stats?.subjects.map((s) => <option key={s} value={s}>{s}</option>)}
        </Select>
      </div>

      {showForm && (
        <Card padding="lg" className="mb-6">
          <form onSubmit={submit} className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-display font-bold text-lg text-ink-900">{editing ? 'Edit' : 'Add'} question</h2>
              <button type="button" onClick={() => setShowForm(false)} className="text-ink-400 hover:text-ink-700">
                <i className="fa-solid fa-xmark text-lg" />
              </button>
            </div>

            {error && (
              <div className="bg-danger-50 text-danger-600 text-sm rounded-xl px-4 py-3 flex items-center gap-2">
                <i className="fa-solid fa-circle-exclamation" /> {error}
              </div>
            )}

            <div className="grid sm:grid-cols-2 gap-3">
              <Input label="Question ID" required placeholder="MTH-0001" value={form.question_id} onChange={(e) => setForm({ ...form, question_id: e.target.value })} disabled={!!editing} hint={editing ? 'Cannot be changed after creation.' : 'Must be unique.'} />
              <Input label="Subject" required value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
              <Input label="Topic" required value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} />
              <Input label="Subtopic" value={form.subtopic} onChange={(e) => setForm({ ...form, subtopic: e.target.value })} />
              <Select label="Difficulty" value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value as Difficulty })}>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </Select>
              <Input label="Exam type" placeholder="JAMB / WAEC / NECO" value={form.exam_type} onChange={(e) => setForm({ ...form, exam_type: e.target.value })} />
              <Input label="Year" placeholder="e.g. 2021 — only for real past questions" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} />
              <Select label="Linked passage" value={form.passage_id} onChange={(e) => setForm({ ...form, passage_id: e.target.value })}>
                <option value="">None</option>
                {passages?.map((p) => <option key={p.passage_id} value={p.passage_id}>{p.passage_id}{p.title ? ` — ${p.title}` : ''}</option>)}
              </Select>
            </div>

            <Textarea label="Question text" required rows={3} value={form.question_text} onChange={(e) => setForm({ ...form, question_text: e.target.value })} />
            <Input label="Image URL" placeholder="Optional — for diagram-based questions" value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} />

            <div className="grid sm:grid-cols-2 gap-3">
              <Input label="Option A" required value={form.option_a} onChange={(e) => setForm({ ...form, option_a: e.target.value })} />
              <Input label="Option B" required value={form.option_b} onChange={(e) => setForm({ ...form, option_b: e.target.value })} />
              <Input label="Option C" required value={form.option_c} onChange={(e) => setForm({ ...form, option_c: e.target.value })} />
              <Input label="Option D" required value={form.option_d} onChange={(e) => setForm({ ...form, option_d: e.target.value })} />
            </div>

            <div className="grid sm:grid-cols-3 gap-3">
              <Select label="Correct option" value={form.correct_option} onChange={(e) => setForm({ ...form, correct_option: e.target.value })}>
                <option value="A">A</option><option value="B">B</option><option value="C">C</option><option value="D">D</option>
              </Select>
              <Select label="Source" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value as QuestionSource })}>
                <option value="original">Original</option>
                <option value="past-question">Past question</option>
                <option value="licensed">Licensed</option>
              </Select>
              <Select label="Status" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as QuestionStatus })}>
                <option value="active">Active</option>
                <option value="draft">Draft</option>
              </Select>
            </div>

            <Textarea label="Explanation" rows={2} value={form.explanation} onChange={(e) => setForm({ ...form, explanation: e.target.value })} />
            <Input label="Tags" placeholder="pipe-separated, e.g. algebra|quadratic" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} />

            <div className="flex gap-2 pt-2">
              <Button type="submit">Save question</Button>
              <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </form>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
        </div>
      ) : questions && questions.length === 0 ? (
        <EmptyState icon="fa-solid fa-inbox" title="No questions found" description="Try a different subject filter, or add one above." />
      ) : (
        <Card padding="none" className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-ink-900 text-white">
              <tr>
                <th className="p-3 text-left font-semibold">ID</th>
                <th className="p-3 text-left font-semibold">Subject / Topic</th>
                <th className="p-3 text-left font-semibold">Question</th>
                <th className="p-3 text-left font-semibold">Difficulty</th>
                <th className="p-3 text-left font-semibold">Status</th>
                <th className="p-3 text-left font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {questions?.map((q) => (
                <tr key={q.id} className="border-t border-ink-100 hover:bg-ink-50/60">
                  <td className="p-3 font-mono text-xs text-ink-500">{q.question_id}</td>
                  <td className="p-3">
                    <div className="font-medium text-ink-800">{q.subject}</div>
                    <div className="text-xs text-ink-400">{q.topic}</div>
                  </td>
                  <td className="p-3 max-w-xs truncate text-ink-700">{q.question_text}</td>
                  <td className="p-3"><DifficultyBadge difficulty={q.difficulty} /></td>
                  <td className="p-3"><StatusBadge status={q.status} /></td>
                  <td className="p-3 whitespace-nowrap">
                    <button onClick={() => openEdit(q)} className="text-brand-600 font-semibold mr-3 hover:underline">Edit</button>
                    <button onClick={() => remove(q.id)} className="text-danger-500 font-semibold hover:underline">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
        </>
      )}
    </div>
  );
}
