import { useState, useRef, useEffect } from 'react'
import { sendChat } from '../services/apiService.js'

function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    // Inject custom CSS for animations and focus states
    const styleElement = document.createElement('style')
    styleElement.id = 'chat-custom-styles'
    styleElement.innerHTML = `
      @keyframes chat-pulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
      }
      .sending-pulse {
        animation: chat-pulse 1.5s infinite ease-in-out;
      }
      .chat-input-focus:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-bg) !important;
      }
      .chat-send-btn:hover:not(:disabled) {
        opacity: 0.9;
        transform: translateY(-1px);
      }
      .chat-send-btn:active:not(:disabled) {
        transform: translateY(0);
      }
    `
    document.head.appendChild(styleElement)
    return () => {
      const el = document.getElementById('chat-custom-styles')
      if (el) el.remove()
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()

    const trimmedInput = input.trim()
    if (!trimmedInput) return

    // Add user message immediately
    setMessages((prev) => [...prev, { sender: 'user', text: trimmedInput }])
    setInput('')
    setError('')
    setLoading(true)

    try {
      const data = await sendChat(trimmedInput)
      if (data && data.response) {
        setMessages((prev) => [...prev, { sender: 'ai', text: data.response }])
      } else {
        setMessages((prev) => [...prev, { sender: 'ai', text: JSON.stringify(data) }])
      }
    } catch (err) {
      console.error(err)
      setError('Error communicating with backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>AI Chat</h1>

      <div style={styles.chatWindow}>
        {messages.length === 0 ? (
          <div style={styles.emptyState}>
            Start a conversation by typing a message below.
          </div>
        ) : (
          <div style={styles.messageList}>
            {messages.map((msg, index) => (
              <div
                key={index}
                style={
                  msg.sender === 'user'
                    ? styles.userMessageContainer
                    : styles.aiMessageContainer
                }
              >
                <div style={styles.senderLabel}>
                  {msg.sender === 'user' ? 'User:' : 'AI:'}
                </div>
                <div
                  style={
                    msg.sender === 'user'
                      ? styles.userMessageBubble
                      : styles.aiMessageBubble
                  }
                >
                  {msg.text}
                </div>
              </div>
            ))}

            {loading && (
              <div style={styles.loadingContainer}>
                <div style={styles.sendingText} className="sending-pulse">
                  Sending...
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {error && <div style={styles.errorText}>{error}</div>}

      <form onSubmit={handleSubmit} style={styles.inputForm}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          style={styles.textInput}
          className="chat-input-focus"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            ...styles.sendButton,
            ...((loading || !input.trim()) ? styles.disabledButton : {}),
          }}
          className="chat-send-btn"
        >
          Send
        </button>
      </form>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: 'calc(100vh - 180px)',
    maxWidth: '850px',
    margin: '20px auto',
    padding: '0 20px',
    boxSizing: 'border-box',
    fontFamily: 'var(--sans)',
  },
  title: {
    fontSize: '36px',
    fontWeight: '600',
    color: 'var(--text-h)',
    margin: '0 0 20px 0',
    textAlign: 'center',
    letterSpacing: '-1px',
  },
  chatWindow: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    border: '1px solid var(--border)',
    borderRadius: '16px',
    backgroundColor: 'var(--bg)',
    padding: '24px',
    overflowY: 'auto',
    boxShadow: 'var(--shadow)',
    marginBottom: '20px',
    position: 'relative',
    minHeight: '300px',
  },
  emptyState: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--text)',
    opacity: 0.7,
    fontSize: '16px',
    fontStyle: 'italic',
  },
  messageList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  userMessageContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    maxWidth: '80%',
    alignSelf: 'flex-end',
  },
  aiMessageContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    maxWidth: '80%',
    alignSelf: 'flex-start',
  },
  senderLabel: {
    fontSize: '12px',
    fontWeight: '600',
    color: 'var(--text)',
    marginBottom: '4px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  userMessageBubble: {
    backgroundColor: 'var(--accent-bg)',
    border: '1px solid var(--accent-border)',
    borderRadius: '16px 16px 2px 16px',
    padding: '12px 18px',
    color: 'var(--text-h)',
    fontSize: '15px',
    lineHeight: '1.5',
    textAlign: 'left',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  aiMessageBubble: {
    backgroundColor: 'var(--code-bg)',
    border: '1px solid var(--border)',
    borderRadius: '16px 16px 16px 2px',
    padding: '12px 18px',
    color: 'var(--text-h)',
    fontSize: '15px',
    lineHeight: '1.5',
    textAlign: 'left',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    alignSelf: 'flex-start',
    marginTop: '10px',
  },
  sendingText: {
    fontStyle: 'italic',
    color: 'var(--text)',
    fontSize: '14px',
    paddingLeft: '4px',
  },
  errorText: {
    color: '#ef4444',
    fontSize: '14px',
    fontWeight: '500',
    textAlign: 'center',
    marginBottom: '12px',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    padding: '10px 16px',
    borderRadius: '8px',
    border: '1px solid rgba(239, 68, 68, 0.2)',
  },
  inputForm: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  textInput: {
    flex: 1,
    padding: '14px 18px',
    border: '1px solid var(--border)',
    borderRadius: '12px',
    fontSize: '16px',
    backgroundColor: 'var(--bg)',
    color: 'var(--text-h)',
    outline: 'none',
    boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.05)',
    transition: 'border-color 0.2s, box-shadow 0.2s',
  },
  sendButton: {
    padding: '14px 28px',
    backgroundColor: 'var(--accent)',
    color: '#fff',
    border: 'none',
    borderRadius: '12px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  disabledButton: {
    backgroundColor: 'var(--border)',
    color: 'var(--text)',
    cursor: 'not-allowed',
    boxShadow: 'none',
    opacity: 0.6,
  },
}

export default Chat
