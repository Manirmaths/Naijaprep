import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import type { QuizResults } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';
import MathText from '../components/ui/MathText';

export default function Results() {
  const { attemptId = '' } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['results', attemptId],
    queryFn: () => api.get<QuizResults>(`/api/quiz/${attemptId}/results`),
  });

  const toggleMark = async (questionId: number, marked: boolean) => {
    await api.post(`/api/review/${questionId}/${marked ? 'unmark' : 'mark'}`);
    queryClient.invalidateQueries({ queryKey: ['results', attemptId] });
  };

  const retakeWrong = async () => {
    try {
      const newAttempt = await api.post<{ attempt_id: number }>(`/api/quiz/${attemptId}/retake-wrong`);
      navigate(`/quiz-attempt/${newAttempt.attempt_id}`);
    } catch {
      alert('Not enough wrong questions to retake (need at least 3).');
    }
  };

  if (isLoading) return <Spinner className="w-8 h-8 mt-16" />;
  if (error || !data) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16">
        <EmptyState icon="fa-solid fa-triangle-exclamation" title="Couldn't load results" />
      </div>
    );
  }

  const pct = data.total > 0 ? Math.round((data.score / data.total) * 100) : 0;
  const tone = pct >= 70 ? 'success' : pct >= 40 ? 'warning' : 'danger';

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="text-center mb-8">
        <h1 className="font-display font-extrabold text-2xl text-ink-900 mb-3">Quiz complete</h1>
        <div
          className={`inline-flex flex-col items-center justify-center w-28 h-28 rounded-full font-display font-extrabold text-2xl ${
            tone === 'success' ? 'bg-success-50 text-success-600' : tone === 'warning' ? 'bg-warning-50 text-warning-600' : 'bg-danger-50 text-danger-600'
          }`}
        >
          {data.score}/{data.total}
          <span className="text-xs font-semibold mt-0.5">{pct}%</span>
        </div>
      </div>

      <div className="flex flex-wrap justify-center gap-3 mb-8">
        <Button variant="outline" onClick={retakeWrong} icon={<i className="fa-solid fa-rotate-left" />}>
          Retake wrong only
        </Button>
        <Link to="/subjects">
          <Button icon={<i className="fa-solid fa-arrow-right" />}>Practice more</Button>
        </Link>
      </div>

      <div className="space-y-3">
        {data.items.map((item, i) => (
          <Card key={item.question_id} padding="md">
            <p className="font-semibold text-ink-900 mb-2 leading-relaxed">
              <span className="text-ink-400 font-normal">{i + 1}.</span> <MathText text={item.question_text} />
            </p>
            {item.image_url && (
              <img src={item.image_url} alt="Question diagram" className="w-full max-h-56 object-contain rounded-lg border border-ink-100 mb-3 bg-ink-50" />
            )}
            <div className="flex flex-wrap gap-2 mb-2">
              <Badge tone={item.is_correct ? 'success' : 'danger'}>Your answer: {item.selected_option}</Badge>
              {!item.is_correct && <Badge tone="success">Correct: {item.correct_option}</Badge>}
            </div>
            {item.explanation && <p className="text-sm text-ink-500 mb-3 leading-relaxed"><MathText text={item.explanation} /></p>}
            <button
              onClick={() => toggleMark(item.question_id, item.is_marked)}
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 inline-flex items-center gap-1"
            >
              <i className={item.is_marked ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark'} />
              {item.is_marked ? 'Unmark' : 'Mark for review'}
            </button>
          </Card>
        ))}
      </div>
    </div>
  );
}
