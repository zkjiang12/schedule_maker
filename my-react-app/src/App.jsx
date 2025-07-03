import { useState } from 'react'
import './App.css'

function App() {
  const [queryContents, setQueryContents] = useState('')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Enhanced markdown parser that recognizes specific AI response patterns
  const parseMarkdown = (text) => {
    if (!text) return ''
    
    let html = text
      // Convert line breaks first
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      
      // Header hierarchy (maintain order - most specific first)
      .replace(/^#### (.+?)$/gm, '<div class="subsection-header">$1</div>')
      .replace(/^### (.+?)$/gm, '<div class="section-header">$1</div>')
      .replace(/^## (.+?)$/gm, '<div class="main-header">$1</div>')
      .replace(/^# (.+?)$/gm, '<div class="main-header">$1</div>')
      
      // Schedule headers (Fall Semester, Spring Semester, etc.)
      .replace(/^\*\*([A-Z][^*:]*(?:Semester|Schedule|Plan)):\*\*$/gm, '<div class="schedule-header">$1</div>')
      
      // Course title blocks (Course Name (CODE):)
      .replace(/^\*\s+\*\*([^*]+)\s*(?:\([^)]+\))?\s*:\*\*$/gm, '<div class="course-title">$1</div>')
      
      // Advice sections
      .replace(/\*My Advice:\*/g, '<div class="advice-label">💡 My Advice:</div><div class="advice-content">')
      .replace(/\*Action Item:\*/g, '<div class="action-label">📋 Action Item:</div><div class="action-content">')
      .replace(/\*Note:\*/g, '<div class="note-label">📝 Note:</div><div class="note-content">')
      
      // Highlight ratings data
      .replace(/\*\*([^*]*(?:quality|difficulty|workload|instructor)[^*]*[0-9.]+\/4\.0[^*]*)\*\*/g, '<span class="rating-highlight">$1</span>')
      
      // Other bold text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      
      // Italic text
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      
      // Lists
      .replace(/^[\s]*\*[\s]+(.+)$/gm, '<li class="bullet-point">$1</li>')
      .replace(/^[\s]*\d+\.[\s]+(.+)$/gm, '<li class="numbered-item">$1</li>')
      
      // Split into sections and wrap
      .split(/\n\s*\n/)
      .map(section => {
        section = section.trim()
        if (!section) return ''
        
        // Check for different section types
        if (section.includes('<li class="numbered-item">')) {
          return `<div class="numbered-list">${section}</div>`
        }
        if (section.includes('<li class="bullet-point">')) {
          return `<div class="bullet-list">${section}</div>`
        }
        if (section.includes('<div class="advice-content">') || 
            section.includes('<div class="action-content">') || 
            section.includes('<div class="note-content">')) {
          return section + '</div>' // Close the content div
        }
        if (section.includes('<div class="')) {
          return section
        }
        
        return `<p>${section.replace(/\n/g, '<br>')}</p>`
      })
      .join('')
      
      // Clean up
      .replace(/(?<!<br>)\n(?!<)/g, ' ')
    
    return html
  }

  const callBackend = async() => {
    if (!queryContents.trim()) return
    
    console.log("fetching")
    setIsLoading(true)
    try{
      const response = await fetch("http://127.0.0.1:5000/",{
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: queryContents })
      })
      
      if (response.ok) {
        const data = await response.text()
        console.log(data)
        setResponse(data)
      } else {
        setResponse('Error: Failed to get response from server')
      }
    }
    catch(err){
      console.log(err)
      setResponse('Error: Could not connect to server')
    }
    finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <div className="container">
        <div className="header-content">
          <h1>Figure Out My Schedule</h1>
          <p>scheduling is way too painful. get AI to do it instead.</p>
        </div>
        <div className="main-content">
          <div className="chat-element">
            <textarea 
              value={queryContents}
              onChange={(e) => setQueryContents(e.target.value)} 
              placeholder="Tell me about your scheduling needs..."
            ></textarea>
            <button onClick={callBackend} disabled={isLoading}>
              {isLoading ? '⏳' : '🔍'}
            </button>
          </div>
          <div className="response-content">
            {response ? (
              <div dangerouslySetInnerHTML={{ __html: parseMarkdown(response) }} />
            ) : (
              <div className="placeholder">
                {isLoading ? 'Processing...' : 'Response will appear here...'}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

export default App
