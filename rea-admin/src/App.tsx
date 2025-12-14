import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Layout from './components/common/Layout';
import PropertiesPage from './pages/Properties/PropertiesPage';
import PropertyEditDynamicPage from './pages/Properties/PropertyEditDynamicPage';
import FieldVisibilityPage from './pages/admin/FieldVisibilityPage';
import ZoningMapPage from './pages/ZoningMap/ZoningMapPage';
import ZohoImportPage from './pages/Import/ZohoImportPage';
import CommandPalette from './components/CommandPalette';
import './styles/globals.css';

function App() {
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
    <Router>
      <Layout onOpenCommandPalette={() => setCommandPaletteOpen(true)}>
        <Routes>
          <Route path="/" element={<PropertiesPage />} />
          <Route path="/properties" element={<PropertiesPage />} />
          <Route path="/properties/:id/edit" element={<PropertyEditDynamicPage />} />
          <Route path="/properties/new" element={<PropertyEditDynamicPage />} />
          <Route path="/admin/field-visibility" element={<FieldVisibilityPage />} />
          <Route path="/map/zoning" element={<ZoningMapPage />} />
          <Route path="/import/zoho" element={<ZohoImportPage />} />
        </Routes>
      </Layout>
      <CommandPalette open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} />
    </Router>
  );
}

export default App;
