import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { api, ApiError } from '../api/client';
import Button from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import Card from '../components/ui/Card';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.post('/api/auth/forgot-password', { email });
      setSent(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16 px-4 sm:px-6">
      <Card padding="lg" className="animate-fade-in">
        <h1 className="font-display font-extrabold text-2xl text-ink-900 text-center mb-1">Forgot your password?</h1>
        <p className="text-center text-sm text-ink-500 mb-6">
          Enter your email and we'll send you a link to reset it.
        </p>

        {error && (
          <div className="bg-danger-50 text-danger-600 text-sm rounded-xl px-4 py-3 mb-4 flex items-center gap-2">
            <i className="fa-solid fa-circle-exclamation" /> {error}
          </div>
        )}

        {sent ? (
          <div className="bg-success-50 text-success-600 text-sm rounded-xl px-4 py-3 flex items-start gap-2">
            <i className="fa-solid fa-circle-check mt-0.5" />
            <span>If that email has an account, a reset link is on its way. Check your inbox (and spam folder).</span>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-4">
            <Input type="email" label="Email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            <Button type="submit" fullWidth size="lg" loading={busy}>
              {busy ? 'Sending…' : 'Send reset link'}
            </Button>
          </form>
        )}

        <p className="text-center text-sm text-ink-500 mt-5">
          <Link to="/login" className="text-brand-600 font-semibold">Back to log in</Link>
        </p>
      </Card>
    </div>
  );
}
