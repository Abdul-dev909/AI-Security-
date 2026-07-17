import { useState, useEffect } from 'react'
import { checkHealth } from '../services/apiService.js'

function Dashboard() {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    let isMounted = true

    const verifyHealth = async () => {
      let isOnline = false
      try {
        const data = await checkHealth()
        if (data && data.status === 'running') {
          isOnline = true
        }
      } catch (error) {
        isOnline = false
      } finally {
        if (isMounted) {
          setStatus(isOnline ? 'online' : 'offline')
        }
      }
    }

    verifyHealth()

    return () => {
      isMounted = false
    }
  }, [])

  return (
    <div>
      <h1>AI Security Dashboard</h1>
      <div>
        {status === 'checking' && <p>Checking backend status...</p>}
        {status === 'online' && <p>Backend Status: Online</p>}
        {status === 'offline' && <p>Backend Status: Offline</p>}
      </div>
    </div>
  )
}

export default Dashboard
