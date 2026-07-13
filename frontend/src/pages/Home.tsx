import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

const FEATURES = [
  {
    icon: 'fa-solid fa-layer-group',
    title: 'Subject & topic practice',
    desc: 'Drill down into any topic across 11 core subjects with instant feedback and explanations.',
  },
  {
    icon: 'fa-solid fa-chart-line',
    title: 'Track your progress',
    desc: 'See exactly which topics need more work with a per-topic accuracy breakdown.',
  },
  {
    icon: 'fa-solid fa-fire',
    title: 'Daily streaks',
    desc: 'Stay consistent — build a practice streak and watch your score climb.',
  },
  {
    icon: 'fa-solid fa-bookmark',
    title: 'Mark for review',
    desc: 'Flag tricky questions and come back to them until they stick.',
  },
];

const SUBJECTS = [
  'Mathematics', 'English', 'Physics', 'Chemistry', 'Biology', 'Geography',
  'Economics', 'Literature', 'Government', 'Commerce', 'Accounting',
];

export default function Home() {
  const { user } = useAuth();

  return (
    <div>
      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-16 pb-20 sm:pt-24 sm:pb-28">
        <div className="max-w-2xl">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 text-brand-700 px-3 py-1 text-xs font-bold mb-5">
            <i className="fa-solid fa-graduation-cap" /> JAMB · WAEC · NECO · Post-UTME
          </span>
          <h1 className="font-display font-extrabold text-4xl sm:text-5xl text-ink-900 leading-tight tracking-tight">
            Practice smarter. <span className="text-brand-500">Walk into exam day ready.</span>
          </h1>
          <p className="mt-5 text-lg text-ink-500 leading-relaxed">
            Naija Prep gives you focused subject and topic practice, clear explanations, and progress
            tracking built specifically for Nigerian students preparing for JAMB, WAEC, NECO and Post-UTME.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link to={user ? '/dashboard' : '/register'}>
              <Button size="lg" icon={<i className="fa-solid fa-arrow-right" />}>
                {user ? 'Go to your dashboard' : 'Start practicing free'}
              </Button>
            </Link>
            {!user && (
              <Link to="/login">
                <Button size="lg" variant="outline">I already have an account</Button>
              </Link>
            )}
          </div>
          <p className="mt-4 text-sm text-ink-400">No card required. Every subject is free to practice.</p>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pb-20">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map((f) => (
            <Card key={f.title}>
              <div className="w-11 h-11 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center text-lg mb-4">
                <i className={f.icon} />
              </div>
              <h3 className="font-display font-bold text-ink-900 mb-1.5">{f.title}</h3>
              <p className="text-sm text-ink-500 leading-relaxed">{f.desc}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* Subjects strip */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pb-24">
        <Card padding="lg" className="bg-ink-900 border-none">
          <div className="flex flex-col lg:flex-row lg:items-center gap-6 justify-between">
            <div>
              <h2 className="font-display font-bold text-2xl text-white mb-2">Every core subject, covered</h2>
              <p className="text-ink-300 text-sm max-w-md">
                From Mathematics to Accounting — practice questions tagged by topic, subtopic and difficulty.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 lg:max-w-md lg:justify-end">
              {SUBJECTS.map((s) => (
                <span key={s} className="text-xs font-semibold text-ink-200 bg-white/10 rounded-full px-3 py-1.5">
                  {s}
                </span>
              ))}
            </div>
          </div>
        </Card>
      </section>
    </div>
  );
}
