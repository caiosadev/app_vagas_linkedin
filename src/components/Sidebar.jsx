import React, { useState, useEffect } from 'react';
import './Sidebar.css';

const Sidebar = ({ activeCategory, setActiveCategory, onOpenProfile, user, onLogout }) => {
  const [minutesLeft, setMinutesLeft] = useState(60 - new Date().getMinutes());

  useEffect(() => {
    const interval = setInterval(() => {
      setMinutesLeft(60 - new Date().getMinutes());
    }, 10000); // Atualiza a cada 10 segundos para não ter lag visual grande
    return () => clearInterval(interval);
  }, []);

  const categories = [
    { id: 'web-designer', label: 'Web Designer', icon: '🎨' },
    { id: 'analista-suporte', label: 'Analista de Suporte', icon: '🛠️' },
    { id: 'analista-atendimento', label: 'Analista de Atendimento', icon: '🎧' },
  ];

  return (
    <aside className="sidebar-container">
      <div className="logo-area">
        <div className="logo-icon">💻</div>
        <div className="logo-text-wrapper">
          <h1 className="logo-text">Vagas Remotas</h1>
          <span className="logo-subtitle">LINKEDIN</span>
        </div>
      </div>

      <nav className="nav-menu">
        <h3 className="nav-title">CATEGORIAS</h3>
        <ul>
          {categories.map((cat) => (
            <li key={cat.id}>
              <button
                className={`nav-btn ${activeCategory === cat.id ? 'active' : ''}`}
                onClick={() => setActiveCategory(cat.id)}
              >
                <span className="icon">{cat.icon}</span>
                <span className="label">{cat.label}</span>
                {activeCategory === cat.id && <div className="active-indicator" />}
              </button>
            </li>
          ))}
        </ul>

        <div className="refresh-section" style={{ textAlign: 'center', padding: '12px', background: 'rgba(255, 255, 255, 0.5)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.8)' }}>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, lineHeight: '1.4' }}>
            <span style={{ display: 'block', fontSize: '1rem', marginBottom: '4px' }}>⏳</span>
            O sistema será atualizado automaticamente em <strong>{minutesLeft} min</strong>.
          </p>
        </div>
      </nav>

      <div className="user-profile">
        <div className="avatar">
          <img src={`https://ui-avatars.com/api/?name=${user ? user.name : 'User'}&background=0284c7&color=fff`} alt="User" />
        </div>
        <div className="user-info">
          <p className="user-name">{user ? user.name : 'Usuário'}</p>
          <button className="profile-action-btn" onClick={onOpenProfile}>
            Meu Perfil e Currículo
          </button>
        </div>
        {user && (
          <button className="logout-action-btn" onClick={onLogout} title="Sair">
            ⎋ Sair
          </button>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
