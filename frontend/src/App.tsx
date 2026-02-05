import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { LandingPage } from './pages/LandingPage';
import { AuthPage } from './pages/AuthPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { AssetsPage } from './pages/AssetsPage';
import { SettingsPage } from './pages/SettingsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Landing Page - marketing site */}
          <Route path="/" element={<LandingPage />} />

          {/* Auth Page - login/signup */}
          <Route path="/login" element={<AuthPage />} />

          {/* App - protected, requires authentication */}
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <Layout>
                  <HomePage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Projects - protected, requires authentication */}
          <Route
            path="/app/projects"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProjectsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Assets - protected, requires authentication */}
          <Route
            path="/app/assets"
            element={
              <ProtectedRoute>
                <Layout>
                  <AssetsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Settings - protected, requires authentication */}
          <Route
            path="/app/settings"
            element={
              <ProtectedRoute>
                <Layout>
                  <SettingsPage />
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
