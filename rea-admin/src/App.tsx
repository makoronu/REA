import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/common/Layout';
import PrivateRoute from './components/common/PrivateRoute';
import { ADMIN_ROLES } from './constants/roles';
import LoginPage from './pages/Auth/LoginPage';
import DevLoginPage from './pages/Auth/DevLoginPage';
import PasswordResetPage from './pages/Auth/PasswordResetPage';
import PropertiesPage from './pages/Properties/PropertiesPage';
import PropertyEditDynamicPage from './pages/Properties/PropertyEditDynamicPage';
import FieldVisibilityPage from './pages/admin/FieldVisibilityPage';
import ZoningMapPage from './pages/ZoningMap/ZoningMapPage';
import ZohoImportPage from './pages/Import/ZohoImportPage';
import ToukiImportPage from './pages/Import/ToukiImportPage';
import IntegrationsPage from './pages/Settings/IntegrationsPage';
import UsersPage from './pages/Settings/UsersPage';
import HelpIndexPage from './pages/Help/HelpIndexPage';
import HelpDetailPage from './pages/Help/HelpDetailPage';
import CommandPalette from './components/CommandPalette';
import './styles/globals.css';

function AppContent() {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  // ⌘K / Ctrl+K でコマンドパレットを開く
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      <Routes>
        {/* 公開ルート */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dev-login" element={<DevLoginPage />} />
        <Route path="/reset-password" element={<PasswordResetPage />} />

        {/* 保護ルート */}
        <Route path="/" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <PropertiesPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/properties" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <PropertiesPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/properties/:id/edit" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <PropertyEditDynamicPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/properties/new" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <PropertyEditDynamicPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/admin/field-visibility" element={
          <PrivateRoute requiredRoles={ADMIN_ROLES}>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <FieldVisibilityPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/map/zoning" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <ZoningMapPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/import/zoho" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <ZohoImportPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/import/touki" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <ToukiImportPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/settings/integrations" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <IntegrationsPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/settings/users" element={
          <PrivateRoute requiredRoles={ADMIN_ROLES}>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <UsersPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/help" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <HelpIndexPage />
            </Layout>
          </PrivateRoute>
        } />
        <Route path="/help/:categoryId" element={
          <PrivateRoute>
            <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
              <HelpDetailPage />
            </Layout>
          </PrivateRoute>
        } />
      </Routes>
      <CommandPalette open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} />
    </>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
