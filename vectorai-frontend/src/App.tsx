import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Camera, Search, X, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Match {
  id: string;
  score: number;
  metadata: {
    name?: string;
    url?: string;
    reference?: string;
    category?: string;
    price?: number;
  };
}

// Agora usamos o caminho relativo, o Nginx faz o roteamento para o backend
const API_BASE_URL = '/api';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [results, setResults] = useState<Match[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [checkDamage, setCheckDamage] = useState(false);
  const [damageResult, setDamageResult] = useState<{ has_damage: boolean; confidence: number } | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
    setResults([]);
    setError(null);
  };

  const handleSearch = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      // 1. Preparar FormData para Busca
      const searchFormData = new FormData();
      searchFormData.append('file', selectedFile);

      // Executar busca de similares - Pegamos apenas o melhor resultado
      const searchRes = await axios.post(`${API_BASE_URL}/search/by-file`, searchFormData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const bestMatches = searchRes.data.matches;
      if (bestMatches && bestMatches.length > 0) {
        setResults([bestMatches[0]]); // Mantém apenas o primeiro (maior score)
      } else {
        setResults([]);
      }

      // 2. Analisar Avaria se solicitado
      if (checkDamage) {
        const damageFormData = new FormData();
        damageFormData.append('file', selectedFile);

        const damageRes = await axios.post(`${API_BASE_URL}/search/analyze/damage`, damageFormData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setDamageResult(damageRes.data);
      } else {
        setDamageResult(null);
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Falha ao processar imagem. Tente novamente ou verifique a conexão.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResults([]);
    setError(null);
    setDamageResult(null);
    setSelectedMatch(null);
  };

  return (
    <div className="container">
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1>VectorAI</h1>
        <p className="subtitle">Busca visual inteligente de produtos</p>
      </motion.header>

      <main className="glass-card">
        {!previewUrl ? (
          <motion.div
            className="upload-zone"
            onClick={() => fileInputRef.current?.click()}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/*"
              style={{ display: 'none' }}
            />
            <div className="upload-content">
              <Camera className="upload-icon" />
              <h3>Tirar Foto ou Upload</h3>
              <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                Toque para abrir a câmera
              </p>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="preview-container">
              <img src={previewUrl} alt="Preview" className="preview-img" />
              <button className="reset-btn" onClick={reset}>
                <X size={20} />
              </button>

              {damageResult && (
                <motion.div
                  initial={{ x: 50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  className={`damage-badge ${damageResult.has_damage ? 'detected' : 'clean'}`}
                >
                  {damageResult.has_damage ? 'Avaria Detectada' : 'Produto Íntegro'}
                  <span>{(damageResult.confidence * 100).toFixed(0)}% conf.</span>
                </motion.div>
              )}
            </div>

            <div className="options-panel">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={checkDamage}
                  onChange={(e) => setCheckDamage(e.target.checked)}
                />
                <span>Verificar Avarias</span>
              </label>
            </div>

            <button
              className="btn"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? (
                <div className="loading-spinner" />
              ) : (
                <>
                  <Search size={20} />
                  Buscar Produtos
                </>
              )}
            </button>
          </motion.div>
        )}

        {error && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ color: '#ef4444', marginTop: '1rem', textAlign: 'center', fontSize: '0.9rem' }}
          >
            {error}
          </motion.p>
        )}
      </main>

      <AnimatePresence>
        {results.length > 0 && (
          <motion.div
            className="results-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <div className="results-header">
              <h2>Melhor Correspondência</h2>
              <button className="reset-link" onClick={reset}>
                <RefreshCw size={16} />
                Nova Busca
              </button>
            </div>
            <div className="results-grid">
              {results.map((match, idx) => (
                <motion.div
                  key={match.id}
                  className="result-card"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.1 }}
                  onClick={() => setSelectedMatch(match)}
                >
                  <div className="result-img-wrapper">
                    <img
                      src={match.metadata.url || 'https://via.placeholder.com/150'}
                      alt={match.metadata.name}
                      className="result-img"
                    />
                  </div>
                  <div className="result-info">
                    <p className="result-name">{match.metadata.name || `Produto ${match.id}`}</p>
                    <div className="result-details">
                      <span className="result-badge id">ID: {match.id}</span>
                      {match.metadata.reference && (
                        <span className="result-badge">Ref: {match.metadata.reference}</span>
                      )}
                      {match.metadata.category && (
                        <span className="result-badge category">{match.metadata.category}</span>
                      )}
                    </div>
                    <p className="result-score">
                      {(match.score * 100).toFixed(1)}% similar
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>

          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {selectedMatch && (
          <div className="modal-overlay" onClick={() => setSelectedMatch(null)}>
            <motion.div
              className="modal-content"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="close-modal" onClick={() => setSelectedMatch(null)}>
                <X size={24} />
              </button>

              <div className="modal-body">
                <div className="comparison-grid">
                  <div className="photo-side">
                    <span className="photo-label">Sua Foto</span>
                    <img src={previewUrl || undefined} alt="Sua captura" className="modal-img captured" />
                  </div>
                  <div className="photo-side">
                    <span className="photo-label">Produto Encontrado</span>
                    <img
                      src={selectedMatch.metadata.url}
                      alt={selectedMatch.metadata.name}
                      className="modal-img matched"
                    />
                  </div>
                </div>

                <div className="modal-info">
                  <h2>{selectedMatch.metadata.name}</h2>
                  <p className="modal-id">ID: {selectedMatch.id}</p>

                  <div className="modal-meta-grid">
                    <div className="meta-item">
                      <span className="label">Referência: </span>
                      <span className="value">{selectedMatch.metadata.reference || '-'}</span>
                    </div>
                    <div className="meta-item">
                      <span className="label">Categoria: </span>
                      <span className="value">{selectedMatch.metadata.category || '-'}</span>
                    </div>
                  </div>

                  {damageResult && (
                    <div className={`modal-damage-status ${damageResult.has_damage ? 'detected' : 'clean'}`}>
                      <div className="status-header">
                        <strong>Status da Avaria:</strong>
                        <span>{(damageResult.confidence * 100).toFixed(0)}% conf.</span>
                      </div>
                      <p>{damageResult.has_damage ? '⚠️ Item com Avaria Detectada' : '✅ Item Íntegro'}</p>
                    </div>
                  )}

                  <div className="modal-actions">
                    <button
                      className="btn return"
                      onClick={() => alert(`Devolução de ${selectedMatch.id} iniciada`)}
                    >
                      Seguir com Devolução
                    </button>
                    <button
                      className="btn salvage"
                      onClick={() => alert(`Direcionado para SALVADO: ${selectedMatch.id}`)}
                    >
                      Direcionar para SALVADO
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
      <style>{`
        .options-panel {
          margin: 1.5rem 0;
          display: flex;
          justify-content: center;
        }
        .toggle-label {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          cursor: pointer;
          font-size: 0.9rem;
          color: var(--text-muted);
          transition: color 0.2s;
        }
        .toggle-label:hover {
          color: var(--text);
        }
        .toggle-label input {
          width: 40px;
          height: 20px;
          appearance: none;
          background: rgba(120, 120, 128, 0.16);
          border-radius: 20px;
          position: relative;
          cursor: pointer;
          transition: background 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .toggle-label input:checked {
          background: #34c759; /* Apple Green */
        }
        .toggle-label input::before {
          content: "";
          position: absolute;
          width: 18px;
          height: 18px;
          background: white;
          border-radius: 50%;
          top: 1px;
          left: 1px;
          transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .toggle-label input:checked::before {
          transform: translateX(20px);
        }
        .reset-btn {
          position: absolute;
          top: 0.5rem;
          right: 0.5rem;
          background: rgba(255, 255, 255, 0.8);
          border: none;
          color: #000;
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          backdrop-filter: blur(4px);
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          z-index: 5;
        }
        .upload-content h3 {
          font-size: 1.1rem;
          font-weight: 600;
          letter-spacing: -0.01em;
        }
        .upload-content p {
          font-size: 0.85rem;
        }
      `}</style>
    </div>
  );
}

export default App;
