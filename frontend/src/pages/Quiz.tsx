import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { api, ApiError } from '../api/client';
import type { QuizAttempt, AnswerResult } from '../api/types';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import ProgressBar from '../components/ui/ProgressBar';
import { DifficultyBadge } from '../components/ui/Badge';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';
import MathText from '../components/ui/MathText';

export default function Quiz() {
  const [params] = useSearchParams();
  const { attemptId: resumeAttemptId } = useParams();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState<QuizAttempt | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<AnswerResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [overallSeconds, setOverallSeconds] = useState<number | null>(null);
  const startedRef = useRef(false);

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;

    const difficulty = params.get('difficulty');
    const year = params.get('year');

    const loadAttempt = resumeAttemptId
      ? api.get<QuizAttempt>(`/api/quiz/${resumeAttemptId}`)
      : api.post<QuizAttempt>('/api/quiz/start', {
          subject: params.get('subject') || undefined,
          topic: params.get('topic') || undefined,
          n: Number(params.get('n') || 5),
          difficulty: difficulty && difficulty !== 'any' ? difficulty : null,
          year: year && year !== 'any' ? year : null,
        });

    loadAttempt
      .then((a) => {
        setAttempt(a);
        if (a.time_limit_seconds) setOverallSeconds(a.time_limit_seconds);
      })
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not start quiz.'))
      .finally(() => setLoading(false));
  }, [params, resumeAttemptId]);

  useEffect(() => {
    if (overallSeconds === null || feedback) return;
    if (overallSeconds <= 0) {
      navigate(attempt ? `/results/${attempt.attempt_id}` : '/subjects');
      return;
    }
    const t = setTimeout(() => setOverallSeconds((s) => (s !== null ? s - 1 : s)), 1000);
    return () => clearTimeout(t);
  }, [overallSeconds, feedback, attempt, navigate]);

  const submitAnswer = async () => {
    if (!attempt?.current_question || !selected) return;
    try {
      const result = await api.post<AnswerResult>(`/api/quiz/${attempt.attempt_id}/answer`, {
        question_id: attempt.current_question.id,
        selected_option: selected,
      });
      setFeedback(result);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not submit answer.');
    }
  };

  const goNext = () => {
    if (!feedback) return;
    if (feedback.next.finished) {
      navigate(`/results/${feedback.next.attempt_id}`);
      return;
    }
    setAttempt(feedback.next);
    setSelected(null);
    setFeedback(null);
  };

  if (loading) return <Spinner className="w-8 h-8 mt-16" />;

  if (error) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16">
        <EmptyState
          icon="fa-solid fa-triangle-exclamation"
          title="Couldn't start this quiz"
          description={error}
          action={<Button onClick={() => navigate('/subjects')}>Back to subjects</Button>}
        />
      </div>
    );
  }

  if (!attempt || !attempt.current_question) return null;

  const q = attempt.current_question;
  const options: [string, string][] = [
    ['A', q.option_a], ['B', q.option_b], ['C', q.option_c], ['D', q.option_d],
  ];

  const fmtTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
      {overallSeconds !== null && (
        <div className="fixed top-20 right-4 sm:right-8 bg-ink-900 text-white font-mono font-bold px-4 py-2 rounded-full shadow-pop z-20 text-sm">
          <i className="fa-regular fa-clock mr-1.5" />
          {fmtTime(Math.max(0, overallSeconds))}
        </div>
      )}

      {q.passage && (
        <Card className="mb-4 bg-brand-50/40 border-brand-100" padding="md">
          {q.passage.title && <h3 className="font-display font-bold text-ink-900 mb-2 text-sm">{q.passage.title}</h3>}
          <p className="text-sm text-ink-600 leading-relaxed whitespace-pre-line">{q.passage.passage_text}</p>
        </Card>
      )}

      <Card padding="lg" className="animate-fade-in">
        <div className="flex justify-between items-center mb-3 gap-3">
          <h2 className="font-display font-bold text-lg text-ink-900">
            Question {attempt.current_index + 1} of {attempt.total}
          </h2>
          <div className="flex items-center gap-2 flex-shrink-0">
            <DifficultyBadge difficulty={q.difficulty} />
            {q.subject && (
              <span className="text-xs bg-ink-100 text-ink-500 rounded-full px-2.5 py-1 font-semibold">{q.subject}</span>
            )}
          </div>
        </div>

        <div className="mb-5">
          <ProgressBar value={(attempt.current_index / attempt.total) * 100} />
        </div>

        <p className="font-semibold text-ink-900 mb-4 leading-relaxed"><MathText text={q.question_text} /></p>

        {q.image_url && (
          <img src={q.image_url} alt="Question diagram" className="w-full max-h-72 object-contain rounded-xl border border-ink-100 mb-4 bg-ink-50" />
        )}

        <div className="space-y-2 mb-5">
          {options.map(([letter, text]) => {
            const isSelected = selected === letter;
            const showFeedback = !!feedback;
            const isCorrectAnswer = showFeedback && feedback.correct_option === letter;
            const isWrongSelected = showFeedback && isSelected && !feedback.is_correct;

            let cls = 'border-ink-200 hover:border-brand-300 hover:bg-brand-50';
            if (showFeedback && isCorrectAnswer) cls = 'border-success-500 bg-success-50';
            else if (isWrongSelected) cls = 'border-danger-400 bg-danger-50';
            else if (isSelected) cls = 'border-brand-500 bg-brand-50';

            return (
              <label key={letter} className={`flex items-center gap-3 border rounded-xl px-4 py-3 cursor-pointer transition-colors ${cls} ${feedback ? 'cursor-default' : ''}`}>
                <input
                  type="radio" name="answer" value={letter} disabled={!!feedback}
                  checked={isSelected} onChange={() => setSelected(letter)}
                  className="accent-brand-500 w-4 h-4"
                />
                <span className="text-sm text-ink-800"><span className="font-bold">{letter}.</span> <MathText text={text} /></span>
                {showFeedback && isCorrectAnswer && <i className="fa-solid fa-circle-check text-success-500 ml-auto" />}
                {isWrongSelected && <i className="fa-solid fa-circle-xmark text-danger-500 ml-auto" />}
              </label>
            );
          })}
        </div>

        {feedback && (
          <div className={`rounded-xl px-4 py-3 mb-4 text-sm ${feedback.is_correct ? 'bg-success-50 text-success-600' : 'bg-warning-50 text-warning-600'}`}>
            <p className="font-semibold mb-1">
              {feedback.is_correct ? 'Correct!' : `Not quite — correct answer is ${feedback.correct_option}.`}
            </p>
            {feedback.explanation && <p className="text-ink-600"><MathText text={feedback.explanation} /></p>}
          </div>
        )}

        {!feedback ? (
          <Button fullWidth size="lg" onClick={submitAnswer} disabled={!selected}>
            Submit answer
          </Button>
        ) : (
          <Button fullWidth size="lg" onClick={goNext}>
            {feedback.next.finished ? 'See 