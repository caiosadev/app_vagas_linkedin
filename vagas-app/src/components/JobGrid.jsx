import React from 'react';
import JobCard from './JobCard';
import './JobGrid.css';

const JobGrid = ({ jobs, categoryName, newJobIds, clearNewJobs, onOpenNewsletter }) => {
  const newJobsCount = jobs.filter(j => newJobIds.has(j.link || j.titulo_vaga)).length;

  return (
    <main className="main-content">
      <header className="main-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Vagas para <span className="highlight">{categoryName}</span> - 100% Remoto</h2>
          <p>
            {jobs.length} oportunidades encontradas.
            {newJobsCount > 0 && (
              <span style={{ marginLeft: '12px', color: '#0284c7', fontWeight: 'bold', background: 'rgba(2, 132, 199, 0.1)', padding: '4px 10px', borderRadius: '12px' }}>
                ✨ {newJobsCount} novas vagas
              </span>
            )}
          </p>
        </div>
        <button 
          className="newsletter-btn" 
          onClick={onOpenNewsletter}
          style={{
            background: 'linear-gradient(135deg, #0284c7, #0369a1)',
            color: '#fff',
            border: 'none',
            padding: '10px 16px',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.9rem',
            boxShadow: '0 4px 12px rgba(2, 132, 199, 0.4)',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
        >
          Receber vagas por E-mail 📩
        </button>
      </header>

      <div className="grid-container" onScroll={() => { if (newJobIds.size > 0) clearNewJobs() }}>
        {jobs.length > 0 ? (
          jobs.map((job, index) => {
            const id = job.link || job.titulo_vaga;
            const isFirstOldJob = newJobsCount > 0 && index === newJobsCount;

            return (
              <React.Fragment key={`${id}-${index}`}>
                {isFirstOldJob && (
                  <div style={{
                    gridColumn: '1 / -1',
                    textAlign: 'center',
                    padding: '16px',
                    color: '#64748b',
                    borderBottom: '1px solid rgba(2, 132, 199, 0.2)',
                    marginBottom: '8px',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '12px'
                  }}>
                    <span style={{ flex: 1, height: '1px', background: 'rgba(2, 132, 199, 0.2)' }}></span>
                    A partir daqui estão as vagas antigas
                    <span style={{ flex: 1, height: '1px', background: 'rgba(2, 132, 199, 0.2)' }}></span>
                  </div>
                )}
                <JobCard job={job} />
              </React.Fragment>
            );
          })
        ) : (
          <div className="empty-state">
            <p>Nenhuma vaga encontrada para esta categoria.</p>
          </div>
        )}
      </div>
    </main>
  );
};

export default JobGrid;
