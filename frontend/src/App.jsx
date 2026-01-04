import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Trash2,
  ChevronRight,
  RotateCcw,
  Mic,
  History,
  FileText,
  CheckCircle2,
  XCircle,
  Lightbulb,
  User,
  Square,
  Github,
  Download,
  HelpCircle
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const App = () => {
  const [feedback, setFeedback] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(() => {
    const saved = localStorage.getItem('requirement_status');
    return saved ? JSON.parse(saved) : null;
  });
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('requirement_history');
    return saved ? JSON.parse(saved) : [];
  });
  const [currentView, setCurrentView] = useState('current'); // 'current' or index
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [audioLevels, setAudioLevels] = useState([]); // Array of audio levels for waveform
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Real requirement state managed in browser
  const [requirementGenome, setRequirementGenome] = useState(() => {
    const saved = localStorage.getItem('requirement_genome');
    return saved ? JSON.parse(saved) : {
      round: 0,
      requirements_summary: '',
      features: [],
      user_stories: [],
      constraints: [],
      clarifications_needed: []
    };
  });

  const pollInterval = useRef(null);
  
  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Set up audio context for visualization
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;
      microphone.connect(analyser);
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      
      // Set up MediaRecorder
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setAudioLevels([]);
      
      // Start visualization
      visualizeAudio();
    } catch (err) {
      console.error("Error starting recording:", err);
      alert("Failed to start recording. Please check microphone permissions.");
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  };
  
  const visualizeAudio = () => {
    if (!analyserRef.current) return;
    
    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    let lastSampleTime = Date.now();
    const sampleInterval = 100; // Sample every 100ms (10fps for 10 seconds = 100 samples)
    
    const updateVisualization = () => {
      if (!analyserRef.current) return;
      
      const now = Date.now();
      
      // Only sample at 10fps (every 100ms) to get 10 seconds of data
      if (now - lastSampleTime >= sampleInterval) {
        analyser.getByteFrequencyData(dataArray);
        
        // Calculate average volume
        const sum = dataArray.reduce((a, b) => a + b, 0);
        const average = sum / bufferLength;
        const normalizedLevel = Math.min(average / 128, 1); // Normalize to 0-1
        
        setAudioLevels(prev => {
          const newLevels = [...prev, normalizedLevel];
          // Keep only last 10 seconds (10fps * 10 seconds = 100 samples)
          const maxSamples = 100;
          return newLevels.slice(-maxSamples);
        });
        
        lastSampleTime = now;
      }
      
      // Continue animation if still recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        animationFrameRef.current = requestAnimationFrame(updateVisualization);
      }
    };
    
    updateVisualization();
  };
  
  const transcribeAudio = async (audioBlob) => {
    setIsTranscribing(true);
    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');
      
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Transcription failed');
      }
      
      const result = await response.json();
      if (result.text) {
        setFeedback(prev => prev + (prev ? ' ' : '') + result.text);
      }
    } catch (err) {
      console.error("Transcription error:", err);
      alert("Failed to transcribe audio. Please try again.");
    } finally {
      setIsTranscribing(false);
    }
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Poll for status
  useEffect(() => {
    if (taskId) {
      pollInterval.current = setInterval(async () => {
        try {
          const res = await fetch(`/api/status/${taskId}`);
          const data = await res.json();
          setStatus(data);

          if (data.status === 'completed' || data.status === 'clarifying') {
            if (data.status === 'completed') {
              clearInterval(pollInterval.current);
              setIsGenerating(false);
              setTaskId(null);
            }
            // Append to local history
            setHistory(prev => [...prev, data]);
            // Update local genome from backend's analysis
            if (data.updated_state) {
              setRequirementGenome(data.updated_state);
            }
          } else if (data.status === 'failed') {
            clearInterval(pollInterval.current);
            setIsGenerating(false);
            setTaskId(null);
            alert("Generation failed: " + data.error);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 3000);
    }
    return () => clearInterval(pollInterval.current);
  }, [taskId]);

  // Persistence
  useEffect(() => {
    localStorage.setItem('requirement_history', JSON.stringify(history));
    localStorage.setItem('requirement_genome', JSON.stringify(requirementGenome));
    localStorage.setItem('requirement_status', JSON.stringify(status));
  }, [history, requirementGenome, status]);

  const handleGenerate = async () => {
    if (!feedback.trim() && requirementGenome.round > 0) return;

    setIsGenerating(true);
    setStatus({ status: 'queued' });

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          feedback: feedback || "请描述你的项目需求...",
          state: requirementGenome
        })
      });
      const data = await res.json();
      setTaskId(data.task_id);
      setFeedback('');
    } catch (err) {
      console.error("Analysis error:", err);
      setIsGenerating(false);
    }
  };

  const downloadJSON = () => {
    if (!status?.document) return;
    const dataStr = JSON.stringify(status.document, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `requirements_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const currentDisplayData = currentView === 'current' ? status : history[currentView];
  const currentGenome = (currentView === 'current' || !history[currentView]?.updated_state)
    ? requirementGenome
    : history[currentView].updated_state;

  return (
    <div className="app-container">
      <header>
        <div className="logo">需求文档<span>生成器</span></div>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          {status?.document && (
            <button
              className="btn-download"
              onClick={downloadJSON}
              title="下载JSON文档"
            >
              <Download size={14} style={{ marginRight: '8px' }} />
              下载文档
            </button>
          )}
          <button
            className="btn-new-session"
            onClick={() => {
              if (window.confirm("开始新会话？这将清除所有历史和需求数据。")) {
                setHistory([]);
                setStatus(null);
                setRequirementGenome({ round: 0, requirements_summary: '', features: [], user_stories: [], constraints: [], clarifications_needed: [] });
                setCurrentView('current');
                localStorage.removeItem('requirement_history');
                localStorage.removeItem('requirement_genome');
                localStorage.removeItem('requirement_status');
              }
            }}
          >
            <RotateCcw size={14} style={{ marginRight: '8px' }} />
            新会话
          </button>
          <a
            href="https://github.com/grapeot/RequirementDocGen"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-github"
            title="View on GitHub"
          >
            <Github size={18} />
          </a>
        </div>
      </header>

      <div className="main-content">
        <div className="discovery-pane">
          {(!currentDisplayData || (!currentDisplayData.document && currentDisplayData.status !== 'clarifying' && !isGenerating)) ? (
            <div className="empty-state">
              <FileText size={48} style={{ marginBottom: '20px', opacity: 0.3 }} />
              <h2>准备生成需求文档？</h2>
              <p>输入你的项目需求，或点击生成按钮开始第1轮分析。</p>
            </div>
          ) : (
            <>
              <div className="section-title">
                第 {currentDisplayData.round} 轮分析
                {currentView !== 'current' && <span style={{ color: 'var(--accent)', marginLeft: '10px' }}>(历史)</span>}
              </div>
              
              {/* Clarifications Needed */}
              {currentDisplayData.clarifications_needed?.length > 0 && (
                <div className="clarifications-box">
                  <div className="clarifications-header">
                    <HelpCircle size={18} style={{ marginRight: '8px' }} />
                    <span>需要澄清的问题</span>
                  </div>
                  <ul className="clarifications-list">
                    {currentDisplayData.clarifications_needed.map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Requirements Document */}
              {currentDisplayData.document && (
                <div className="requirements-document">
                  {/* Project Info */}
                  {currentDisplayData.document.project && (
                    <div className="document-section">
                      <h3 className="section-heading">项目信息</h3>
                      <div className="project-info">
                        <h4>{currentDisplayData.document.project.name}</h4>
                        <p>{currentDisplayData.document.project.description}</p>
                      </div>
                    </div>
                  )}

                  {/* User Stories */}
                  {currentDisplayData.document.user_stories?.length > 0 && (
                    <div className="document-section">
                      <h3 className="section-heading">用户故事</h3>
                      <div className="user-stories-list">
                        {currentDisplayData.document.user_stories.map((story, i) => (
                          <div key={i} className="user-story-card">
                            <div className="story-header">
                              <span className="story-id">{story.id}</span>
                              <span className={`priority-badge priority-${story.priority || 'medium'}`}>
                                {story.priority || 'medium'}
                              </span>
                            </div>
                            <h4 className="story-title">{story.title}</h4>
                            <p className="story-description">{story.description}</p>
                            {story.acceptance_criteria?.length > 0 && (
                              <div className="acceptance-criteria">
                                <strong>验收标准：</strong>
                                <ul>
                                  {story.acceptance_criteria.map((criteria, j) => (
                                    <li key={j}>{criteria}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Features */}
                  {currentDisplayData.document.features?.length > 0 && (
                    <div className="document-section">
                      <h3 className="section-heading">功能特性</h3>
                      <div className="features-list">
                        {currentDisplayData.document.features.map((feature, i) => (
                          <div key={i} className="feature-card">
                            <div className="feature-header">
                              <span className="feature-id">{feature.id}</span>
                              <h4>{feature.name}</h4>
                            </div>
                            <p>{feature.description}</p>
                            {feature.related_user_stories?.length > 0 && (
                              <div className="related-stories">
                                <strong>相关用户故事：</strong>
                                {feature.related_user_stories.join(', ')}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Constraints */}
                  {currentDisplayData.document.constraints?.length > 0 && (
                    <div className="document-section">
                      <h3 className="section-heading">约束条件</h3>
                      <ul className="constraints-list">
                        {currentDisplayData.document.constraints.map((constraint, i) => (
                          <li key={i} className="constraint-item">
                            <XCircle size={14} style={{ marginRight: '8px', color: '#ff6666' }} />
                            {constraint}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        <div className="sidebar">
          <div className="sidebar-item">
            <div className="section-title"><FileText size={16} /> 需求状态</div>

            {currentGenome.requirements_summary && (
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '15px', borderRadius: '12px', marginBottom: '20px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--accent)', marginBottom: '8px', letterSpacing: '1px', textTransform: 'uppercase' }}>
                  <User size={10} style={{ marginRight: '5px' }} /> AI 摘要
                </div>
                <div style={{ fontSize: '0.85rem', lineHeight: '1.6', color: '#ccc' }}>
                  <ReactMarkdown>{currentGenome.requirements_summary}</ReactMarkdown>
                </div>
              </div>
            )}

            <div style={{ marginBottom: '15px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '5px' }}>功能特性</div>
              <div className="tag-list">
                {currentGenome.features?.map((feature, i) => (
                  <div key={i} className="tag"><CheckCircle2 size={10} color="var(--exploitation)" /> {feature}</div>
                ))}
                {(!currentGenome.features || currentGenome.features.length === 0) && <span style={{ fontSize: '0.7rem', color: '#555' }}>暂无数据</span>}
              </div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '5px' }}>约束条件</div>
              <div className="tag-list">
                {currentGenome.constraints?.map((constraint, i) => (
                  <div key={i} className="tag"><XCircle size={10} color="#ff6666" /> {constraint}</div>
                ))}
                {(!currentGenome.constraints || currentGenome.constraints.length === 0) && <span style={{ fontSize: '0.7rem', color: '#555' }}>暂无数据</span>}
              </div>
            </div>
            {currentGenome.clarifications_needed?.length > 0 && (
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '5px' }}>待澄清问题</div>
                <div className="tag-list">
                  {currentGenome.clarifications_needed.map((q, i) => (
                    <div key={i} className="tag clarification-tag">
                      <HelpCircle size={10} style={{ marginRight: '5px' }} />
                      {q}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="sidebar-item">
            <div className="section-title"><History size={16} /> 分析历史</div>
            <div className="history-list">
              <div
                className={`history-item ${currentView === 'current' ? 'active' : ''}`}
                onClick={() => setCurrentView('current')}
              >
                当前轮次 {status?.round || requirementGenome.round}
              </div>
              {[...history]
                .reverse()
                .filter(h => h.round !== (status?.round || requirementGenome.round))
                .map((h) => {
                  const originalIndex = history.indexOf(h);
                  return (
                    <div
                      key={originalIndex}
                      className={`history-item ${currentView === originalIndex ? 'active' : ''}`}
                      onClick={() => setCurrentView(originalIndex)}
                    >
                      第 {h.round} 轮存档
                    </div>
                  );
                })}
            </div>
          </div>

          <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
            <Lightbulb size={16} />
            提示：请详细描述功能需求、用户角色和使用场景。
          </div>
        </div>
      </div>

      <div className="controls">
        <div className="input-wrapper">
          {isRecording && (
            <div className="waveform-container">
              <div className="waveform">
                {audioLevels.map((level, i) => (
                  <div
                    key={i}
                    className="waveform-bar"
                    style={{
                      height: `${Math.max(level * 100, 5)}%`,
                      backgroundColor: `rgba(44, 107, 237, ${0.3 + level * 0.7})`
                    }}
                  />
                ))}
              </div>
            </div>
          )}
          <textarea
            placeholder={requirementGenome.round === 0 ? "描述你的项目需求，或点击生成按钮开始..." : requirementGenome.clarifications_needed?.length > 0 ? "回答上述澄清问题..." : "继续补充需求信息..."}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            disabled={isGenerating || isRecording}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleGenerate();
              }
            }}
          />
          <div style={{ position: 'absolute', right: '20px', bottom: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
            {isTranscribing && (
              <div className="transcribing-indicator">
                <div className="loader" style={{ width: 16, height: 16, borderWidth: 2 }}></div>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent)', marginLeft: '8px' }}>Transcribing...</span>
              </div>
            )}
            <button
              className={`btn-voice ${isRecording ? 'recording' : ''} ${isTranscribing ? 'transcribing' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isGenerating || isTranscribing}
              title={isRecording ? "Stop recording" : isTranscribing ? "Transcribing..." : "Start voice input"}
            >
              {isRecording ? <Square size={24} /> : isTranscribing ? <div className="loader" style={{ width: 20, height: 20, borderWidth: 2 }} /> : <Mic size={20} />}
            </button>
          </div>
        </div>
        <button
          className="btn-generate"
          onClick={handleGenerate}
          disabled={isGenerating || isRecording}
        >
          {isGenerating ? <div className="loader" style={{ width: 24, height: 24, borderWidth: 2 }} /> : <Sparkles size={32} />}
        </button>
      </div>

      {isGenerating && (
        <div className="status-overlay">
          <div className="loader"></div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--accent)', letterSpacing: '1px', textTransform: 'uppercase', fontWeight: 700 }}>
              {status?.status === 'completed' ? '已完成' : status?.status === 'clarifying' ? '需要澄清' : (status?.status || 'AI分析中...')}
            </span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>分析需求并生成文档...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
