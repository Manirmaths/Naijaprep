import { Link } from 'react-router-dom';
import Button from '../components/ui/Button';

export default function NotFound() {
  return (
    <div className="text-center py-28 px-4">
      <p className="font-display font-extrabold text-6xl text-brand-200 mb-2">404</p>
      <h1 className="font-display font-bold text-2xl text-ink-900 mb-6">Page not found</h1>
      <Link to="/">
        <Button>Go home</Button>
      </Link>
    </div>
  );
}
