import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/common/Layout';
import PropertiesPage from './pages/Properties/PropertiesPage';
import PropertyEditDynamicPage from './pages/Properties/PropertyEditDynamicPage';
// import ToukiImportPage from './pages/Import/ToukiImportPage';
import './styles/globals.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<PropertiesPage />} />
          <Route path="/properties" element={<PropertiesPage />} />
          <Route path="/properties/:id/edit" element={<PropertyEditDynamicPage />} />
          <Route path="/properties/new" element={<PropertyEditDynamicPage />} />
          {/* <Route path="/import/touki" element={<ToukiImportPage />} /> */}
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;