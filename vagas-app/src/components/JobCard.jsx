import React, { useState, useEffect } from 'react';
import './JobCard.css';

const JobCard = ({ job }) => {
  const [isApplied, setIsApplied] = useState(false);

  useEffect(() => {
    if (job.link) {
      const appliedJobs = JSON.parse(localStorage.getItem('applied_jobs') || '[]');
      if (appliedJobs.includes(job.link)) {
        setIsApplied(true);
      }
    }
  }, [job.link]);

  const handleApplyClick = () => {
    if (job.link) {
      const appliedJobs = JSON.parse(localStorage.getItem('applied_jobs') || '[]');
      if (!appliedJobs.includes(job.link)) {
        appliedJobs.push(job.link);
        localStorage.setItem('applied_jobs', JSON.stringify(appliedJobs));
      }
      setIsApplied(true);
    }
  };

  return (
    <div className={`glass-card job-card ${job.match_score > 0 ? 'highlight-match' : (job.match_score === 0 ? 'no-match' : '')}`}>
      {job.match_score > 0 && (
        <div className="match-banner">
          🎯 Enquadra no seu perfil em {Number(job.match_score).toFixed(1)}%
        </div>
      )}
      {job.match_score === 0 && (
        <div className="no-match-banner">
          🚫 Essa vaga não se enquadra ao seu perfil
        </div>
      )}
      
      <div className="job-header">
        <div className="company-logo">
          {job.logo_empresa ? (
            <img src={job.logo_empresa} alt={`Logo ${job.nome_empresa}`} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          ) : (
            job.nome_empresa.charAt(0).toUpperCase()
          )}
        </div>
        <div className="job-meta" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <span className="date-badge">Nova</span>
            {job.candidaturas && job.candidaturas !== 'Não informado' && (
              <span className="applicants-badge">
                👥 {job.candidaturas}
              </span>
            )}
          </div>
        </div>
      </div>
      
      <div className="job-content">
        <h3 className="job-title">{job.titulo_vaga}</h3>
        <p className="job-company">
          {job.nome_empresa === 'Não informada' || job.nome_empresa === 'Não informado' 
            ? 'Nome da Empresa: Não Informada' 
            : job.nome_empresa}
        </p>
      </div>

      <div className="job-footer">
        <div className="job-salary">
          <span className="icon">💰</span>
          <span>{job.salario === 'Não publicado na listagem' || !job.salario ? 'Salário não informado' : job.salario}</span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="location-badge">Vaga: 🇧🇷</span>
          {job.link ? (
            <a 
              href={job.link} 
              target="_blank" 
              rel="noopener noreferrer" 
              className={`apply-btn ${isApplied ? 'applied' : ''}`}
              onClick={handleApplyClick}
            >
              {isApplied ? 'Você já clicou nesta vaga' : 'Candidatar-se'}
            </a>
          ) : (
            <button className="apply-btn disabled">Ver Vaga</button>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobCard;
