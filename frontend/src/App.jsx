import { useState, useEffect, useRef } from 'react';
import './App.css';
import { chatWithDocuments, checkHealth } from './api';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState([]);
  const [health, setHealth] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Check backend health on mount
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unhealthy' }));
  }, []);

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Convert messages to history format
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await chatWithDocuments(input, history);

      const assistantMessage = {
        role: 'assistant',
        content: response.response
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSources(response.sources || []);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        role: 'error',
        content: `Error: ${error.message || 'Failed to get response'}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>
          RAG Documentation Assistant
          {health && (
            <span
              className={`health-indicator ${health.status === 'healthy' ? 'healthy' : 'unhealthy'}`}
              title={`Status: ${health.status}`}
            />
          )}
        </h1>
      </header>

      <div className="main-content">
        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 ? (
              <div className="empty-state">
                Ask a question about your documentation...
              </div>
            ) : (
              messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  {message.content}
                </div>
              ))
            )}
            {loading && <div className="loading">Thinking...</div>}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              disabled={loading}
            />
            <button onClick={handleSend} disabled={loading || !input.trim()}>
              Send
            </button>
          </div>
        </div>

        <div className="sources-panel">
          <h2>Sources</h2>
          {sources.length === 0 ? (
            <p style={{ color: '#999', fontSize: '0.9rem' }}>
              No sources yet. Start a conversation to see relevant documents.
            </p>
          ) : (
            sources.map((source, index) => (
              <div key={index} className="source-item">
                <h3>
                  {source.metadata?.source_type || 'Unknown'}: {source.metadata?.source_id || 'N/A'}
                </h3>
                <div className="source-text">
                  {source.text.substring(0, 150)}
                  {source.text.length > 150 ? '...' : ''}
                </div>
                <div className="source-meta">
                  Score: {source.score?.toFixed(3) || 'N/A'}
                  {source.metadata?.url && (
                    <>
                      {' | '}
                      <a href={source.metadata.url} target="_blank" rel="noopener noreferrer">
                        View Source
                      </a>
                    </>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
