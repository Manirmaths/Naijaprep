import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api, ApiError } from '../api/client';
import Button from '../components/ui/Button';
import { PasswordInput } from '../components/ui/Input';
import Card from '../components/ui/Card';
import EmptyState from '../components/ui/EmptyState';

export default function ResetPassword() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get('token') || '';

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  if (!token) {
    return (
      <div className="max-w-md mx-auto mt-16 px-4 sm:px-6">
        <EmptyState
          icon="fa-solid fa-triangle-exclamation"
          title="Missing reset link"
          description="This page needs a reset token from the email link. Request a new one below."
          action={<Link to="/forgot-password"><Button>Request reset link</Button></Link>}
        />
      </div>
    );
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setBusy(true);
    try {
      await api.post('/api/auth/reset-password', { token, password });
      setDone(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16 px-4 sm:px-6">
      <Card padding="lg" className="animate-fade-in">
        <h1 className="font-display font-extrabold text-2xl text-ink-900 text-center mb-1">Set a new password</h1>
        <p className="text-center text-sm text-ink-500 mb-6">Choose a new password for your account.</p>

        {error && (
          <div className="bg-danger-50 text-danger-600 text-sm rounded-xl px-4 py-3 mb-4 flex items-center gap-2">
            <i className="fa-solid fa-circle-exclamation" /> {error}
          </div>
        )}

        {done ? (
          <div className="bg-success-50 text-success-600 text-sm rounded-xl px-4 py-3 flex items-start gap-2">
            <i className="fa-solid fa-circle-check mt-0.5" />
            <span>Password reset. Taking you to log in…</span>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-4">
            <PasswordInput label="New password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" />
            <PasswordInput label="Confirm new password" required minLength={8} value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="••••••••" />
            <Button type="submit" fullWidth size="lg" loading={busy}>
              {busy ? 'Resetting…' : 'Reset password'}
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
}
