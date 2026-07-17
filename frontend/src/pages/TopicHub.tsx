import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { api, ApiError } from '../api/client';
import type { LessonNote, NoteTutorResponse } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Select } from '../components/ui/Input';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';
import NoteContent from '../components/ui/NoteContent';

interface ChatTurn {
  question: string;
  reply: string;
}

function TutorPanel({ subject, topic }: { subject: string; topic: string }) {
  const [message, setMessage] = useState('');
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);

  const ask = async () => {
    const q = message.trim();
    if (!q || sending) return;
    setSending(true);
    setError(null);
    try {
      const res = await api.post<NoteTutorResponse>(`/api/notes/${encodeURIComponent(subject)}/${encodeURIComponent(topic)}/tutor`, {
        message: q,
      });
      setTurns((t) => [...t, { question: q, reply: res.reply }]);
      setRemaining(res.queries_remaining_today);
      setMessage('');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not reach the AI tutor.');
    } finally {
      setSending(false);
    }
  };

  return (
    <Card padding="lg">
      <h2 className="font-display font-bold text-ink-900 mb-1">
        <i className="fa-solid fa-wand-magic-sparkles text-brand-500 mr-1.5" />
        Ask the AI tutor
      </h2>
      <p className="text-xs text-ink-500 mb-4">
        Stuck on something in this note? Ask a quick question — replies are kept short.
        {remaining !== null && <span className="text-ink-400"> ({remaining} left today)</span>}
      </p>

      {turns.length > 0 && (
        <div className="space-y-3 mb-4">
          {turns.map((t, i) => (
            <div key={i} className="space-y-1.5">
              <p className="text-sm font-semibold text-ink-700 bg-ink-50 rounded-lg px-3 py-2">{t.question}</p>
              <p className="text-sm text-ink-700 leading-relaxed bg-brand-50 rounded-lg px-3 py-2">{t.reply}</p>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && ask()}
          placeholder="e.g. why does that formula work?"
          className="flex-1 min-w-[180px] text-sm rounded-lg border border-ink-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-200"
        />
        <Button size="sm" onClick={ask} disabled={sending || !message.trim()}>
          {sending ? 'Asking…' : 'Ask'}
        </Button>
      </div>
      {error && <p className="text-xs text-danger-500 mt-1.5">{error}</p>}
    </Card>
  );
}

export default function TopicHub() {
  const { subject = '', topic = '' } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [n, setN] = useState('10');

  const { data, isLoading, error } = useQuery({
    queryKey: ['note', subject, topic],
    queryFn: () => api.get<LessonNote>(`/api/notes/${encodeURIComponent(subject)}/${encodeURIComponent(topic)}`),
    retry: false,
  });

  useEffect(() => {
    if (data && !data.is_read) {
      api.post(`/api/notes/${encodeURIComponent(subject)}/${encodeURIComponent(topic)}/read`).then(() => {
        queryClient.invalidateQueries({ queryKey: ['note', subject, topic] });
        queryClient.invalidateQueries({ queryKey: ['learn-hub'] });
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data?.id]);

  const vote = async (isHelpful: boolean) => {
    await api.post(`/api/notes/${encodeURIComponent(subject)}/${encodeURIComponent(topic)}/feedback`, { is_helpful: isHelpful });
    queryClient.invalidateQueries({ queryKey: ['note', subject, topic] });
  };

  const startQuiz = () => {
    navigate(`/quiz?subject=${encodeURIComponent(subject)}&topic=${encodeURIComponent(topic)}&n=${n}`);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <nav className="text-sm text-ink-400 mb-3">
        <Link to="/subjects" className="hover:text-brand-600">Subjects</Link>
        <span className="mx-1.5">/</span>
        <Link to={`/subjects/${encodeURIComponent(subject)}`} className="hover:text-brand-600">{subject}</Link>
        <span className="mx-1.5">/</span>
        <span className="text-ink-600 font-medium">{topic}</span>
      </nav>

      {isLoading && <Spinner className="w-8 h-8 mt-8" />}

      {error && (
        <EmptyState
          icon="fa-solid fa-book-open"
          title="No lesson note here yet"
          description="This topic doesn't have a published note yet — you can still practice it directly."
          action={
            <Link to={`/quiz?subject=${encodeURIComponent(subject)}&topic=${encodeURIComponent(topic)}&n=10`}>
              <Button>Practice this topic</Button>
            </Link>
          }
        />
      )}

      {data && (
        <>
          <div className="mb-6">
            <span className="inline-block text-xs bg-ink-100 text-ink-500 rounded-full px-2.5 py-1 font-semibold mb-2">
              {subject}
            </span>
            <h1 className="font-display font-extrabold text-2xl text-ink-900">{data.title}</h1>
            {data.summary && <p className="text-ink-500 mt-1.5">{data.summary}</p>}
          </div>

          {data.glossary.length > 0 && (
            <Card padding="lg" className="mb-6 bg-ink-50 border-ink-100">
              <h2 className="font-display font-bold text-sm text-ink-900 mb-3">
                <i className="fa-solid fa-book text-brand-500 mr-1.5" />
                Key terms
              </h2>
              <dl className="grid sm:grid-cols-2 gap-x-6 gap-y-3">
                {data.glossary.map((g) => (
                  <div key={g.term}>
                    <dt className="font-semibold text-sm text-ink-800">{g.term}</dt>
                    <dd className="text-sm text-ink-500">{g.definition}</dd>
                  </div>
                ))}
              </dl>
            </Card>
          )}

          <Card padding="lg" className="mb-6">
            <NoteContent content={data.content_md} />
          </Card>

          {data.related_topics.length > 0 && (
            <Card padding="lg" className="mb-6">
              <h2 className="font-display font-bold text-sm text-ink-900 mb-3">Study next</h2>
              <div className="flex flex-wrap gap-2">
                {data.related_topics.map((t) => (
                  <Link
                    key={t}
                    to={`/subjects/${encodeURIComponent(subject)}/topics/${encodeURIComponent(t)}`}
                    className="text-sm font-semibold text-brand-700 bg-brand-50 hover:bg-brand-100 rounded-full px-3.5 py-1.5 transition-colors"
                  >
                    {t} <i className="fa-solid fa-arrow-right ml-1 text-xs" />
                  </Link>
                ))}
              </div>
            </Card>
          )}

          <div className="flex items-center justify-between mb-6 px-1">
            <p className="text-xs text-ink-400 font-medium">Was this note helpful?</p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => vote(true)}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm transition-colors ${
                  data.my_feedback === true ? 'bg-success-500 text-white' : 'bg-ink-100 text-ink-400 hover:text-ink-600'
                }`}
                aria-label="Helpful"
              >
                <i className="fa-solid fa-thumbs-up" />
              </button>
              <button
                onClick={() => vote(false)}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm transition-colors ${
                  data.my_feedback === false ? 'bg-danger-500 text-white' : 'bg-ink-100 text-ink-400 hover:text-ink-600'
                }`}
                aria-label="Not helpful"
              >
                <i className="fa-solid fa-thumbs-down" />
              </button>
            </div>
          </div>

          <Card padding="lg" className="mb-6 bg-brand-50 border-brand-100">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="font-display font-bold text-ink-900">Ready to practice?</p>
                <p className="text-sm text-ink-600 mt-0.5">Test yourself on {topic} now, while it's fresh.</p>
              </div>
              <div className="flex items-center gap-2">
                <Select value={n} onChange={(e) => setN(e.target.value)} className="!w-auto !py-2">
                  <option value="5">5 Qs</option>
                  <option value="10">10 Qs</option>
                  <option value="20">20 Qs</option>
                </Select>
                <Button onClick={startQuiz} icon={<i className="fa-solid fa-play" />}>
                  Start quiz
                </Button>
              </div>
            </div>
          </Card>

          <TutorPanel subject={subject} topic={topic} />
        </>
      )}
    </div>
  );
}
