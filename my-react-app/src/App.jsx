import { useState } from 'react'
import './App.css'

function App() {
  const [queryContents, setQueryContents] = useState('')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Enhanced markdown parser with better formatting
  const parseMarkdown = (text) => {
    if (!text) return ''
    
    let html = text
      // Convert line breaks to proper spacing first
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      
      // Headers with proper hierarchy
      .replace(/^### \*\*(.+?)\*\*$/gm, '<div class="subsection-header">$1</div>')
      .replace(/^### (.+?)$/gm, '<div class="subsection-header">$1</div>')
      .replace(/^## \*\*(.+?)\*\*$/gm, '<div class="section-header">$1</div>')
      .replace(/^## (.+?)$/gm, '<div class="section-header">$1</div>')
      .replace(/^# \*\*(.+?)\*\*$/gm, '<div class="main-header">$1</div>')
      .replace(/^# (.+?)$/gm, '<div class="main-header">$1</div>')
      
      // Course information blocks
      .replace(/^(\*\*[^*]+\*\*)\s*\(([^)]+)\):\s*(.+)$/gm, 
        '<div class="course-card"><h4>$1 ($2)</h4><p>$3</p></div>')
      
      // Bold and italic text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      
      // Lists - handle both bullets and numbers
      .replace(/^[\s]*[-*+]\s+(.+)$/gm, '<li class="bullet-point">$1</li>')
      .replace(/^[\s]*\d+\.\s+(.+)$/gm, '<li class="numbered-item">$1</li>')
      
      // Paragraphs - split by double newlines
      .split(/\n\s*\n/)
      .map(para => {
        para = para.trim()
        if (!para) return ''
        
        // Check if it's a list
        if (para.includes('<li class="bullet-point">')) {
          return `<div class="bullet-list">${para}</div>`
        }
        if (para.includes('<li class="numbered-item">')) {
          return `<div class="numbered-list">${para}</div>`
        }
        
        // Check if it's already formatted (headers, course cards, etc.)
        if (para.includes('<div class="') || para.includes('<h')) {
          return para
        }
        
        // Regular paragraph
        return `<p>${para.replace(/\n/g, '<br>')}</p>`
      })
      .join('')
      
      // Clean up any remaining single newlines in non-pre content
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
