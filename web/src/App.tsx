import { useState, useEffect } from 'react'
import './App.css'
import axios from 'axios'
import api, { checkBackend } from './api'

type User = {
  id: number
  first_name: string
  last_name: string
  email: string
  role: string
}

function App() {
  const [backendConnected, setBackendConnected] = useState(false)
  const [checkingBackend, setCheckingBackend] = useState(true)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState('')
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function verifyBackend() {
      try {
        await checkBackend()
        setBackendConnected(true)
      } catch {
        setBackendConnected(false)
      } finally {
        setCheckingBackend(false)
      }
    }

    verifyBackend()
  }, [])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')

    try {
      const loginResponse = await api.post('/auth/login-user', {
        email,
        password,
      })

      setToken(loginResponse.data.access_token)

      const meResponse = await api.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${loginResponse.data.access_token}`,
        },
      })

      setUser(meResponse.data)
    } catch (error) {
      if (axios.isAxiosError(error) && !error.response) {
        setError('Backend is not running')
      } else {
        setError('Invalid email or password')
      }
    }
  }

  function handleLogout() {
    setEmail('')
    setError('')
    setPassword('')
    setToken('')
    setUser(null)
  }

  return (
    <main>
      <h1>Barbershop App</h1>

      {!user && (
        <form onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={!backendConnected || checkingBackend}
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={!backendConnected || checkingBackend}
            />
          </label>

          <button
            type="submit"
            disabled={!backendConnected || checkingBackend}
          >
            Login
          </button>
        </form>
      )}

      {checkingBackend && <p>Checking backend connection...</p>}
      {!checkingBackend && !backendConnected && <p>Backend is not running.</p>}

      {token && <p>Logged in successfully</p>}

      {user && (
        <>
          <p>Welcome back, {user.first_name}</p>
          <button onClick={handleLogout}>Logout</button>
        </>
      )}

      {error && <p>{error}</p>}
    </main>
  )
}

export default App
