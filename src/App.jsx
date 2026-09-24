import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import JobGrid from './components/JobGrid';
import ProfileModal from './components/ProfileModal';
import AuthModal from './components/AuthModal';
import DonateModal from './components/DonateModal';
import ContactModal from './components/ContactModal';
import NewsletterModal from './components/NewsletterModal';
import fallbackJobs from './vagasData.json';

function App() {
  const [user, setUser] = useState(null);
  const [activeCategory, setActiveCategory] = useState('web-designer');
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  const [newJobIds, setNewJobIds] = useState(new Set());
  const [isDonateModalOpen, setIsDonateModalOpen] = useState(false);
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [isNewsletterModalOpen, setIsNewsletterModalOpen] = useState(false);

  useEffect(() => {
    // Tenta recuperar o usuário logado
    const savedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }

    // Verifica se a URL contém o link de doação
    if (window.location.hash === '#apoie') {
      setIsDonateModalOpen(true);
      // Remove o hash da URL para ficar limpo
      window.history.replaceState(null, null, window.location.pathname);
    }
  }, []);

  const fetchVagas = async () => {
    try {
      const response = await fetch('/api/vagas');
      if (response.ok) {
        const data = await response.json();
        
        // Helper function to extract number from candidaturas string
        const parseCandidaturas = (str) => {
          if (!str || str === 'Não informado') return 999999;
          const num = parseInt(str.replace(/\D/g, ''), 10);
          return isNaN(num) ? 999999 : num;
        };

        // Sort data by candidaturas ascending
        const sortedData = data.sort((a, b) => parseCandidaturas(a.candidaturas) - parseCandidaturas(b.candidaturas));

        setJobs(prevJobs => {
          if (prevJobs.length > 0) {
            const prevJobLinks = new Set(prevJobs.map(j => j.link || j.titulo_vaga));
            const newJobsList = sortedData.filter(j => !prevJobLinks.has(j.link || j.titulo_vaga));
            if (newJobsList.length > 0) {
              const ids = newJobsList.map(j => j.link || j.titulo_vaga);
              setNewJobIds(prev => new Set([...prev, ...ids]));
            }
          }
          
          if (prevJobs.length === 0) return sortedData;
          
          return sortedData.map(newJob => {
            const oldJob = prevJobs.find(pj => pj.link === newJob.link);
            if (oldJob && oldJob.match_score !== undefined) {
              return { ...newJob, match_score: oldJob.match_score };
            }
            return newJob;
          });
        });
      }
    } catch (error) {
      console.error("Erro ao carregar as vagas:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVagas();
    const interval = setInterval(fetchVagas, 30000);
    return () => clearInterval(interval);
  }, []);

  const [refreshRemaining, setRefreshRemaining] = useState(0);

  useEffect(() => {
    const checkCooldown = () => {
      const lastRefresh = localStorage.getItem('last_refresh');
      if (lastRefresh) {
        const elapsed = (Date.now() - parseInt(lastRefresh, 10)) / 1000;
        const remaining = (15 * 60) - elapsed;
        if (remaining > 0) {
          setRefreshRemaining(Math.ceil(remaining / 60));
        } else {
          setRefreshRemaining(0);
          localStorage.removeItem('last_refresh');
        }
      }
    };
    checkCooldown();
    const interval = setInterval(checkCooldown, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const response = await fetch('/api/refresh', { method: 'POST' });
      const data = await response.json();
      
      if (response.status === 202) {
        localStorage.setItem('last_refresh', Date.now());
        setRefreshRemaining(15);
        alert(data.message);
      } else if (response.status === 429) {
        // O servidor avisa que não pode, podemos tentar extrair o tempo ou apenas setar um tempo de fallback
        alert(data.message);
        // Como fallback, se não tivermos no localStorage, colocamos 15m (não ideal, mas evita spam)
        if (!localStorage.getItem('last_refresh')) {
           localStorage.setItem('last_refresh', Date.now());
           setRefreshRemaining(15);
        }
      } else {
        alert(data.message || "Erro desconhecido ao tentar atualizar.");
      }
    } catch (error) {
      console.error("Erro ao solicitar atualização:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleProfileAnalysis = (scoresMap) => {
    setJobs(prevJobs => {
      return prevJobs.map(job => {
        const link = job.link || job.titulo_vaga;
        // Se a vaga está no map, recebe o score, caso contrário, recebe 0 (não se enquadra)
        if (scoresMap[link] !== undefined) {
          return { ...job, match_score: scoresMap[link] };
        }
        return { ...job, match_score: 0 };
      });
    });
  };

  useEffect(() => {
    // Se o usuário está logado, tem perfil (linkedin ou resume), e existem vagas que ainda não têm match_score
    if (user && (user.linkedin_url || user.has_resume) && jobs.length > 0) {
      const hasUnscoredJobs = jobs.some(job => job.match_score === undefined);
      if (hasUnscoredJobs) {
        const autoAnalyze = async () => {
          try {
            const token = localStorage.getItem('token');
            if (!token) return;
            const formData = new FormData();
            
            // Enviamos a URL do linkedin que o front já sabe que o usuário tem
            if (user.linkedin_url) {
              formData.append('linkedinUrl', user.linkedin_url);
            }
            // O backend já pega o PDF do banco de dados automaticamente
            
            const response = await fetch('/api/analyze', {
              method: 'POST',
              headers: { 'Authorization': `Bearer ${token}` },
              body: formData
            });
            const data = await response.json();
            if (response.ok) {
              handleProfileAnalysis(data.scores);
            }
          } catch (e) {
            console.error("Erro na auto-análise:", e);
          }
        };
        autoAnalyze();
      }
    }
  }, [jobs, user]);

  const filteredJobs = jobs.filter(job => {
    if (!job) return false;
    
    const term = (job.termo_busca || "").toLowerCase();
    const title = (job.titulo_vaga || "").toLowerCase();

    if (activeCategory === 'web-designer') {
      return title.includes('web design') || 
             title.includes('webdesign') || 
             title.includes('designer web') ||
             (title.includes('vaga via post') && term.includes('web designer'));
    }
    if (activeCategory === 'analista-suporte') {
      return title.includes('suporte') || 
             title.includes('help desk') || 
             title.includes('helpdesk') || 
             title.includes('service desk') ||
             title.includes('technical support') ||
             title.includes('tech support') ||
             (title.includes('vaga via post') && term.includes('suporte'));
    }
    if (activeCategory === 'analista-atendimento') {
      return title.includes('atendimento') || 
             title.includes('customer service') || 
             title.includes('customer success') || 
             title.includes('customer experience') ||
             title.includes('sucesso do cliente') ||
             title.includes('experiência do cliente') ||
             title.includes('relacionamento') ||
             (title.includes('vaga via post') && term.includes('atendimento'));
    }
    return false;
  }).sort((a, b) => {
    const idA = a.link || a.titulo_vaga;
    const idB = b.link || b.titulo_vaga;
    const isNewA = newJobIds.has(idA) ? 1 : 0;
    const isNewB = newJobIds.has(idB) ? 1 : 0;
    
    if (isNewA !== isNewB) {
      return isNewB - isNewA;
    }
    
    const scoreA = a.match_score || 0;
    const scoreB = b.match_score || 0;
    return scoreB - scoreA;
  });

  let finalJobs = filteredJobs;
  if (finalJobs.length === 0) {
    // Fallback: se o scraper da última hora não trouxe vagas para a categoria, exibe vagas cacheadas locais
    finalJobs = fallbackJobs.filter(job => {
      if (!job) return false;
      const term = (job.termo_busca || "").toLowerCase();
      const title = (job.titulo_vaga || "").toLowerCase();
      
      if (activeCategory === 'web-designer') {
        return title.includes('design') || title.includes('ux') || title.includes('ui');
      }
      if (activeCategory === 'analista-suporte') {
        return title.includes('suporte') || title.includes('desk') || title.includes('support');
      }
      if (activeCategory === 'analista-atendimento') {
        return title.includes('atendimento') || title.includes('customer');
      }
      return false;
    }).slice(0, 50); // Limita para não pesar a UI com o fallback inteiro
  }

  const categoryLabels = {
    'web-designer': 'Web Designer',
    'analista-suporte': 'Analista de Suporte',
    'analista-atendimento': 'Analista de Atendimento'
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setUser(null);
  };

  const clearNewJobs = () => setNewJobIds(new Set());

  return (
    <>
    {!user && <AuthModal onLoginSuccess={(userData) => setUser(userData)} />}

    <div className="layout-wrapper">
      <div className="app-container glass-panel">
        <Sidebar 
          activeCategory={activeCategory} 
          setActiveCategory={setActiveCategory}
          onOpenProfile={() => setIsProfileModalOpen(true)}
          user={user}
          onLogout={handleLogout}
        />
        
        {isLoading ? (
          <div className="main-content" style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
            <p>Carregando vagas...</p>
          </div>
        ) : (
          <JobGrid 
            jobs={finalJobs} 
            categoryName={categoryLabels[activeCategory]} 
            newJobIds={newJobIds}
            clearNewJobs={clearNewJobs}
            onOpenNewsletter={() => setIsNewsletterModalOpen(true)}
          />
        )}
      </div>

      <footer className="app-footer">
        <span className="footer-credit">
          Desenvolvido por <a href="https://visuals.com.br" target="_blank" rel="noopener noreferrer" className="footer-link" style={{ fontWeight: 600 }}>Visuals</a> & <a href="https://www.linkedin.com/in/caiosadev" target="_blank" rel="noopener noreferrer" className="footer-link" style={{ fontWeight: 600 }}>@caiosadev</a>
        </span>
        <div className="footer-links">
          <a href="#" className="footer-link donate-link" onClick={(e) => { e.preventDefault(); setIsDonateModalOpen(true); }}>Projeto Open Source, faça sua doação aqui.</a>
          <a href="#" className="footer-link" onClick={(e) => { e.preventDefault(); setIsContactModalOpen(true); }}>Contato</a>
          <a href="/tutorial.html" target="_blank" rel="noopener noreferrer" className="footer-link">Como Usar</a>
          <a href="/docs.html" target="_blank" rel="noopener noreferrer" className="footer-link">Documentação</a>
        </div>
      </footer>
    </div>
    
    <ProfileModal 
      isOpen={isProfileModalOpen} 
      onClose={() => setIsProfileModalOpen(false)}
      onAnalyze={handleProfileAnalysis}
      token={localStorage.getItem('token')}
    />

    <DonateModal 
      isOpen={isDonateModalOpen} 
      onClose={() => setIsDonateModalOpen(false)} 
    />

    <ContactModal 
      isOpen={isContactModalOpen} 
      onClose={() => setIsContactModalOpen(false)} 
    />

    <NewsletterModal
      isOpen={isNewsletterModalOpen}
      onClose={() => setIsNewsletterModalOpen(false)}
    />
    </>
  );
}

export default App;
