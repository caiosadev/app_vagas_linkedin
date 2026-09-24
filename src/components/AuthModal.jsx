import React, { useState } from 'react';
import './AuthModal.css';

const AuthModal = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    login: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Erro na autenticação');
      }

      if (isLogin) {
        // Salva o token e dados do usuário
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        onLoginSuccess(data.user);
      } else {
        // Se registrou com sucesso, muda para a aba de login
        setIsLogin(true);
        setError('Conta criada com sucesso! Faça login para continuar.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay auth-overlay">
      <div className="modal-content glass-card auth-card">
        <h2>{isLogin ? 'Bem-vindo de volta 👋' : 'Criar Conta ✨'}</h2>
        <p className="modal-desc">
          {isLogin 
            ? 'Faça login para acessar suas vagas e analisar seu perfil.' 
            : 'Crie sua conta gratuita para salvar seu currículo e perfil.'}
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <>
              <div className="form-group">
                <label>Nome Completo</label>
                <input 
                  type="text" 
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="glass-input" 
                  required 
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input 
                  type="email" 
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="glass-input" 
                  required 
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>Login (Usuário)</label>
            <input 
              type="text" 
              name="login"
              value={formData.login}
              onChange={handleChange}
              className="glass-input" 
              required 
            />
          </div>

          <div className="form-group">
            <label>Senha</label>
            <input 
              type="password" 
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="glass-input" 
              required 
            />
          </div>

          {error && <div className={`error-msg ${error.includes('sucesso') ? 'success-msg' : ''}`}>{error}</div>}

          <button type="submit" className="submit-btn" disabled={isLoading}>
            {isLoading ? 'Processando...' : (isLogin ? 'Entrar' : 'Cadastrar')}
          </button>
        </form>

        <div className="auth-switch">
          {isLogin ? 'Ainda não tem conta? ' : 'Já possui uma conta? '}
          <button type="button" onClick={() => { setIsLogin(!isLogin); setError(''); }}>
            {isLogin ? 'Cadastre-se' : 'Faça Login'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
