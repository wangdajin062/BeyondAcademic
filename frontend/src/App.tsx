import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './components/LoginPage';
import { ArticleList } from './components/ArticleList';
import { AcademicEditor } from './components/AcademicEditor';
import { NavBar } from './components/NavBar';
import WorkflowApp from './components/WorkflowApp';
import PaperWritingPlatform from './components/PaperWritingPlatform';
import LiteratureList from './components/LiteratureList';
import './styles/app.css';

const App: React.FC = () => (
  <BrowserRouter>
    <div className="app-shell">
      <NavBar />
      <div className="app-content">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/articles" element={<ArticleList />} />
          <Route path="/editor/:articleId" element={<AcademicEditor />} />
          <Route path="/workflows/*" element={<WorkflowApp />} />
          <Route path="/write/:articleId" element={<PaperWritingPlatform />} />
          <Route path="/literature" element={<LiteratureList />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </div>
  </BrowserRouter>
);

export default App;
