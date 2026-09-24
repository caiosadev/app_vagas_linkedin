import React, { useState } from 'react';
import './ContactModal.css';

const ContactModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: 'Entrar em contato',
    message: '',
    bot_field: '' // Honeypot field for antispam
  });
  const [status, setStatus] = useState('idle'); // 'idle', 'submitting', 'success', 'error'
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Honeypot check (Antispam)
    if (formData.bot_field) {
      // If honeypot is filled, silently reject it as spam
      setStatus('success');
      return;
    }

    setStatus('submitting');
    setErrorMsg('');

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setFormData({ name: '', email: '', subject: 'Entrar em contato', message: '', bot_field: '' });
        setTimeout(() => {
          setStatus('idle');
          onClose();
        }, 3000);
      } else {
        setStatus('error');
        setErrorMsg(data.error || 'Erro ao enviar a mensagem. Tente novamente.');
      }
    } catch (error) {
      setStatus('error');
      setErrorMsg('Falha na comunicação com o servidor.');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content contact-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>&times;</button>
        
        <div className="contact-header">
          <h2>Fale Conosco 💬</h2>
          <p>Envie suas dúvidas, relate bugs ou sugira novas ideias.</p>
        </div>

        {status === 'success' ? (
          <div className="contact-success">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <h3>Mensagem enviada!</h3>
            <p>Obrigado pelo contato. Retornaremos em breve.</p>
          </div>
        ) : (
          <form className="contact-form" onSubmit={handleSubmit}>
            {/* Honeypot field (hidden from users) */}
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
                placeholder="Seu nome"
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
              <label>Assunto</label>
              <select name="subject" value={formData.subject} onChange={handleChange} required>
                <option value="Entrar em contato">Entrar em contato</option>
                <option value="Enviar bugs">Relatar um bug</option>
                <option value="Enviar ideias e melhorias">Enviar ideias e melhorias</option>
              </select>
            </div>

            <div className="form-group">
              <label>Mensagem</label>
              <textarea 
                name="message" 
                required 
                rows="4" 
                placeholder="Como podemos te ajudar?"
                value={formData.message}
                onChange={handleChange}
              ></textarea>
            </div>

            {status === 'error' && <p className="contact-error">{errorMsg}</p>}

            <button type="submit" className="submit-btn" disabled={status === 'submitting'}>
              {status === 'submitting' ? 'Enviando...' : 'Enviar Mensagem'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default ContactModal;
