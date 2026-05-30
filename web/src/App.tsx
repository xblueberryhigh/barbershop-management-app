import { useState } from 'react'
import './App.css'
import api from './api'

type User = {
  id: number
  first_name: string
  last_name: string
  email: string
  role: string
}

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState('')
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState('')

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')

    try {
      const loginResponse = await api.post('/auth/login-user', {
        email,
        password, 
      })

      console.log(loginResponse.data)
      setToken(loginResponse.data.access_token)

      const meResponse = await api.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${loginResponse.data.access_token}`,
        },
      })

      console.log(meResponse.data)
      setUser(meResponse.data)
    } catch {
      setError('Login failed')
    }
  }

  function handleLogout(){
      setEmail('')
      setError('')
      setPassword('')
      setToken('')
      setUser(null)
  }

  return (
    <main>
      <h1>Barbershop App</h1>

      {!user && (<form onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        <button type="submit">Login</button>
      </form>)}

      {token && <p>Logged in successfully</p>}
      {user && <p>Welcome back, {user.first_name}</p>}
      {user && <button onClick={handleLogout}>Logout</button>}
      {error && <p>{error}</p>}
    </main>
  )
}

export default App