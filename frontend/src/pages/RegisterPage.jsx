import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'

function RegisterPage({ onRegister }) {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('dj')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await axios.post('/api/auth/register', {
        email,
        password,
        role,
      })

      const { user, token } = response.data
      onRegister(user, token)
      navigate(user.role === 'admin' ? '/admin' : '/dj')
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Musikwunsch DJ App</h1>
        <p style={styles.subtitle}>Create Account</p>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={styles.input}
              disabled={loading}
            />
          </div>

          <div style={styles.formGroup}>
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={styles.input}
              disabled={loading}
            />
          </div>

          <div style={styles.formGroup}>
            <label>Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              style={styles.input}
              disabled={loading}
            >
              <option value="dj">DJ</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <button
            type="submit"
            style={styles.button}
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p style={styles.login}>
          Already have an account? <Link to="/login" style={styles.link}>Login here</Link>
        </p>
      </div>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  card: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    width: '100%',
    maxWidth: '400px',
  },
  title: {
    textAlign: 'center',
    color: '#1F4E78',
    marginBottom: '10px',
  },
  subtitle: {
    textAlign: 'center',
    color: '#666',
    marginBottom: '30px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  input: {
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
  },
  button: {
    padding: '12px',
    backgroundColor: '#FF6B35',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  error: {
    backgroundColor: '#fee',
    color: '#c33',
    padding: '10px',
    borderRadius: '4px',
    marginBottom: '20px',
  },
  login: {
    textAlign: 'center',
    marginTop: '20px',
    color: '#666',
  },
  link: {
    color: '#FF6B35',
    textDecoration: 'none',
  },
}

export default RegisterPage
