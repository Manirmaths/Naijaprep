import { Routes, Route } from 'react-router-dom';
import PublicLayout from './components/PublicLayout';
import AppShell from './components/AppShell';
import RequireAuth from './components/RequireAuth';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Subjects from './pages/Subjects';
import SubjectTopics from './pages/SubjectTopics';
import Quiz from './pages/Quiz';
import Results from './pages/Results';
import Dashboard from './pages/Dashboard';
import Leaderboard from './pages/Leaderboard';
import Blitz from './pages/Blitz';
import Mock from './pages/Mock';
import Review from './pages/Review';
import Admin from './pages/Admin';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<NotFound />} />
      </Route>

      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/subjects" element={<Subjects />} />
        <Route path="/subjects/:subject" element={<SubjectTopics />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/quiz-attempt/:attemptId" element={<Quiz />} />
        <Route path="/results/:attemptId" element={<Results />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/blitz" element={<Blitz />} />
        <Route path="/mock" element={<Mock />} />
        <Route path="/review" element={<Review />} />
        <Route
          path="/admin"
          element={
            <RequireAuth adminOnly>
              <Admin />
            </RequireAuth>
          }
        />
      </Route>
    </Routes>
  );
}
