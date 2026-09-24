import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './ProfileModal.css';

const ProfileModal = ({ isOpen, onClose, onAnalyze, token }) => {
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [resumePdf, setResumePdf] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasResumeSaved, setHasResumeSaved] = useState(false);

  useEffect(() => {
    if (isOpen && token) {
      // Carregar dados salvos
      fetch('/api/user/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(data => {
        if (data.linkedin_url) setLinkedinUrl(data.linkedin_url);
        if (data.has_resume) setHasResumeSaved(true);
      })
      .catch(console.error);
    }
  }, [isOpen, token]);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('O currículo deve estar no formato PDF.');
        setResumePdf(null);
        return;
      }
      setResumePdf(file);
      setError('');
    }
  };

  const removeFile = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setResumePdf(null);
    setHasResumeSaved(false); // Força ele a enviar um novo
  };

  const saveProfile = async () => {
    const formData = new FormData();
    formData.append('linkedinUrl', linkedinUrl || '');
    if (resumePdf) formData.append('resumePdf', resumePdf);
    if (!resumePdf && !hasResumeSaved) formData.append('removeResume', 'true');

    await fetch('/api/user/profile', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!linkedinUrl && !resumePdf && !hasResumeSaved) {
      setError('Preencha o link do LinkedIn ou envie o seu currículo em PDF.');
      return;
    }

    setIsLoading(true);

    try {
      // Salva primeiro no banco
      await saveProfile();

      // Roda análise
      const formData = new FormData();
      formData.append('linkedinUrl', linkedinUrl || '');
      if (resumePdf) formData.append('resumePdf', resumePdf);
      if (!resumePdf && !hasResumeSaved) formData.append('removeResume', 'true');

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      
      const data = await response.json();

      if (response.ok) {
        onAnalyze(data.scores);
        onClose();
      } else {
        setError(data.message || 'Erro ao analisar o perfil.');
      }
    } catch (err) {
      setError('Erro de conexão com o servidor.');
    } finally {
      setIsLoading(false);
    }
  };

  const modalContent = (
    <div className="modal-overlay">
      <div className="modal-content glass-card">
        <button className="close-btn" onClick={onClose}>&times;</button>
        
        <h2>Análise de Perfil e Match 🎯</h2>
        <p className="modal-desc">
          Vamos cruzar as suas experiências com as descrições das vagas e trazer as mais compatíveis para o topo!
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Link do Perfil do LinkedIn (Opcional)</label>
            <input 
              type="url" 
              className="glass-input"
              placeholder="https://www.linkedin.com/in/seuperfil/"
              value={linkedinUrl}
              onChange={(e) => setLinkedinUrl(e.target.value)}
            />
          </div>

          <div className="form-group" style={{ marginTop: '32px' }}>
            <label>Currículo em PDF (Recomendado)</label>
            {!resumePdf && !hasResumeSaved ? (
              <label className="file-label">
                <input 
                  type="file" 
                  accept="application/pdf"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
                <span className="icon">📄</span>
                <span>Selecionar arquivo PDF...</span>
              </label>
            ) : (
              <div className="file-selected-state">
                <div style={{display: 'flex', alignItems: 'center', flex: 1}}>
                  <div className="icon">📄</div>
                  <span className="file-name">
                    {resumePdf ? resumePdf.name : 'Currículo Salvo.pdf'}
                  </span>
                </div>
                <button className="remove-file-btn" onClick={removeFile} title="Remover Arquivo">
                  &times;
                </button>
              </div>
            )}
          </div>

          {error && <div className="error-msg">{error}</div>}

          <button type="submit" className="submit-btn" disabled={isLoading}>
            {isLoading ? 'Processando...' : 'Analisar meu perfil'}
          </button>
        </form>
      </div>
    </div>
  );

  return ReactDOM.createPortal(
    modalContent,
    document.body
  );
};

export default ProfileModal;
