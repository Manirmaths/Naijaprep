import { Routes, Route } from 'react-router-dom';
import PublicLayout from './components/PublicLayout';
import AppShell from './components/AppShell';
import RequireAuth from './components/RequireAuth';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import PrivacyPolicy from './pages/PrivacyPolicy';
import Subjects from './pages/Subjects';
import SubjectTopics from './pages/SubjectTopics';
import Quiz from './pages/Quiz';
import Results from './pages/Results';
import Dashboard from './pages/Dashboard';
import Leaderboard from './pages/Leaderboard';
import Blitz from './pages/Blitz';
import Mock from './pages/Mock';
import Achievements from './pages/Achievements';
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
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
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
        <Route path="/achievements" element={<Achievements />} />
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
