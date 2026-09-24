import React, { useState } from 'react';
import './DonateModal.css';

const DonateModal = ({ isOpen, onClose }) => {
  const [copied, setCopied] = useState(false);
  const pixKey = '1ef67cfd-6d20-41aa-960a-37af9bc06a19';

  const handleCopy = () => {
    navigator.clipboard.writeText(pixKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content donate-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>&times;</button>

        <div className="donate-header">
          <h2>Apoie o Projeto 💙</h2>
          <p>Este é um projeto Open Source! Sua doação é o maior incentivo para continuarmos dedicando tempo ao desenvolvimento de novas funcionalidades e melhorias na plataforma. Qualquer valor faz a diferença!</p>
        </div>

        <div className="pix-image-container">
          <img src="/pix-qrcode.png" alt="QR Code Pix" className="pix-image" style={{ maxWidth: '200px' }} />
        </div>

        <div className="pix-copy-section">
          <p className="pix-label">Ou copie a chave aleatória (PIX):</p>
          <div className="pix-input-group">
            <input
              type="text"
              readOnly
              value={pixKey}
              className="pix-input"
            />
            <button className={`copy-btn ${copied ? 'copied' : ''}`} onClick={handleCopy}>
              {copied ? 'Copiado!' : 'Copiar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DonateModal;
