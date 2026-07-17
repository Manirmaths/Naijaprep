import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

const FEATURES = [
  {
    icon: 'fa-solid fa-layer-group',
    title: 'Subject & topic practice',
    desc: 'Drill down into any topic across 11 core subjects with instant feedback and clear explanations.',
  },
  {
    icon: 'fa-solid fa-file-signature',
    title: 'Full JAMB mock exam',
    desc: 'The real UTME format — English plus 3 subjects of your choice, 180 questions, one 120-minute timer.',
  },
  {
    icon: 'fa-solid fa-wand-magic-sparkles',
    title: 'AI tutor',
    desc: "Stuck on a question you got wrong? Ask the AI tutor for a different explanation, in simple language.",
  },
  {
    icon: 'fa-solid fa-clock-rotate-left',
    title: 'Smart Review',
    desc: 'Spaced repetition that quietly resurfaces exactly what you\'re about to forget, right before you forget it.',
  },
  {
    icon: 'fa-solid fa-chart-line',
    title: 'Track your progress',
    desc: 'A per-topic accuracy breakdown, a projected JAMB score, and a "focus on this" list of your weak spots.',
  },
  {
    icon: 'fa-solid fa-bolt',
    title: 'Blitz Challenge',
    desc: 'Three minutes, one subject, no mercy — a quick-fire round for when you only have a few minutes to spare.',
  },
  {
    icon: 'fa-solid fa-fire',
    title: 'Daily streaks & goals',
    desc: 'Set a daily XP goal, build a streak, and earn streak freezes that protect it if you miss a day.',
  },
  {
    icon: 'fa-solid fa-medal',
    title: 'Achievements & leaderboard',
    desc: 'Unlock badges as you practice, and see how you stack up against everyone else on Naija Prep.',
  },
];

const STEPS = [
  {
    n: '1',
    title: 'Pick a subject or topic',
    desc: 'Choose exactly what to practice — a full subject, one topic, a past-question year, or let Smart Review pick for you.',
  },
  {
    n: '2',
    title: 'Answer, get instant feedback',
    desc: 'Every question comes with an explanation. Get it wrong and the AI tutor can explain it a different way.',
  },
  {
    n: '3',
    title: 'Track progress, stay consistent',
    desc: 'Your dashboard shows what to focus on next, a projected score, and keeps your streak alive.',
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
            Naija Prep gives you focused subject and topic practice, an AI tutor, a full JAMB CBT mock,
            spaced-repetition review, and progress tracking built specifically for Nigerian students.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link to={user ? '/dashboard' : '/register'}>
              <Button size="lg" icon={<i className="fa-solid fa-arrow-right" />}>
                {user ? 'Go to your dashboard' : 'Start free practice'}
              </Button>
            </Link>
            <Link to={user ? '/mock' : '/register'}>
              <Button size="lg" variant="outline" icon={<i className="fa-solid fa-file-signature" />}>
                Take a mock CBT
              </Button>
            </Link>
          </div>
          <p className="mt-4 text-sm text-ink-400">No card required. Every subject is free to practice.</p>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-6xl mx-auto px-4 sm:px-6 pb-20 scroll-mt-20">
        <div className="max-w-xl mb-8">
          <h2 className="font-display font-extrabold text-2xl sm:text-3xl text-ink-900">Everything you need to prepare</h2>
          <p className="text-ink-500 mt-2">Not just a question bank — a full study system.</p>
        </div>
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

      {/* How it works */}
      <section id="how-it-works" className="max-w-6xl mx-auto px-4 sm:px-6 pb-20 scroll-mt-20">
        <div className="max-w-xl mb-8">
          <h2 className="font-display font-extrabold text-2xl sm:text-3xl text-ink-900">How it works</h2>
          <p className="text-ink-500 mt-2">Three steps, no complicated setup.</p>
        </div>
        <div className="grid sm:grid-cols-3 gap-6">
          {STEPS.map((s) => (
            <div key={s.n} className="relative">
              <div className="w-10 h-10 rounded-full bg-ink-900 text-white flex items-center justify-center font-display font-extrabold text-sm mb-4">
                {s.n}
              </div>
              <h3 className="font-display font-bold text-ink-900 mb-1.5">{s.title}</h3>
              <p className="text-sm text-ink-500 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Subjects strip */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pb-20">
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

      {/* Final CTA */}
      {!user && (
        <section className="max-w-6xl mx-auto px-4 sm:px-6 pb-24">
          <Card padding="lg" className="bg-brand-50 border-brand-100 text-center">
            <h2 className="font-display font-extrabold text-2xl text-ink-900 mb-2">Ready to start practicing?</h2>
            <p className="text-ink-600 mb-6 max-w-md mx-auto">
              Create a free account and get your first topic breakdown in under two minutes.
            </p>
            <Link to="/register">
              <Button size="lg" icon={<i className="fa-solid fa-arrow-right" />}>Get started free</Button>
            </Link>
          </Card>
        </section>
      )}
    </div>
  );
}
