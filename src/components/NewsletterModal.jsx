import React, { useState } from 'react';
import './NewsletterModal.css';

const NewsletterModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    frequency: '1x',
    bot_field: '' // Honeypot
  });
  const [selectedAreas, setSelectedAreas] = useState([]);
  const [status, setStatus] = useState('idle');
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleAreaChange = (e) => {
    const value = e.target.value;
    setSelectedAreas(prev => 
      prev.includes(value) 
        ? prev.filter(a => a !== value) 
        : [...prev, value]
    );
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.bot_field) {
      setStatus('success');
      return;
    }

    if (selectedAreas.length === 0) {
      setStatus('error');
      setErrorMsg('Por favor, selecione ao menos uma área de interesse.');
      return;
    }

    setStatus('submitting');
    setErrorMsg('');

    try {
      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          areas: selectedAreas
        })
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setFormData({ name: '', email: '', frequency: '1x', bot_field: '' });
        setSelectedAreas([]);
        setTimeout(() => {
          setStatus('idle');
          onClose();
        }, 3000);
      } else {
        setStatus('error');
        setErrorMsg(data.error || 'Erro ao cadastrar. Tente novamente.');
      }
    } catch (error) {
      setStatus('error');
      setErrorMsg('Falha na comunicação com o servidor.');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content newsletter-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>&times;</button>
        
        <div className="newsletter-header">
          <h2>Receba Vagas no E-mail 📩</h2>
          <p>Fique por dentro das melhores oportunidades selecionadas pelo nosso sistema de inteligência artificial.</p>
        </div>

        {status === 'success' ? (
          <div className="newsletter-success">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <h3>Inscrição Confirmada!</h3>
            <p>Você começará a receber nossas seleções de vagas no seu e-mail.</p>
          </div>
        ) : (
          <form className="newsletter-form" onSubmit={handleSubmit}>
            <input 
              type="text" 
              name="bot_field" 
              value={formData.bot_field} 
              onChange={handleChange} 
              style={{ display: 'none' }} 
              tabIndex="-1" 
              autoComplete="off" 
            />

            <div className="form-group">
              <label>Nome Completo</label>
              <input 
                type="text" 
                name="name" 
                required 
                placeholder="Ex: João da Silva"
                value={formData.name}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>E-mail</label>
              <input 
                type="email" 
                name="email" 
                required 
                placeholder="seu@email.com"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Frequência de Recebimento</label>
              <select name="frequency" value={formData.frequency} onChange={handleChange} required>
                <option value="1x">1x ao dia (Resumo Diário)</option>
                <option value="3x">3x ao dia (Manhã, Tarde e Noite)</option>
                <option value="5x">5x ao dia (Atualizações Frequentes)</option>
              </select>
            </div>

            <div className="form-group checkbox-group">
              <label style={{ display: 'block', marginBottom: '10px' }}>Áreas de Interesse (Selecione 1 ou mais)</label>
              <div className="checkboxes-container">
                <label className="checkbox-label">
                  <input type="checkbox" value="Web Design" checked={selectedAreas.includes("Web Design")} onChange={handleAreaChange} />
                  <span>Web Design</span>
                </label>
                <label className="checkbox-label">
                  <input type="checkbox" value="Suporte e Atendimento" checked={selectedAreas.includes("Suporte e Atendimento")} onChange={handleAreaChange} />
                  <span>Suporte e Atendimento</span>
                </label>
                <label className="checkbox-label">
                  <input type="checkbox" value="Vagas Gerais" checked={selectedAreas.includes("Vagas Gerais")} onChange={handleAreaChange} />
                  <span>Vagas Gerais / Remoto (Feed)</span>
                </label>
              </div>
            </div>

            {status === 'error' && <p className="newsletter-error">{errorMsg}</p>}

            <button type="submit" className="submit-btn" disabled={status === 'submitting'}>
              {status === 'submitting' ? 'Cadastrando...' : 'Quero Receber Vagas'}
            </button>
            <p className="newsletter-privacy">Não enviamos spam. Você pode cancelar quando quiser.</p>
          </form>
        )}
      </div>
    </div>
  );
};

export default NewsletterModal;
