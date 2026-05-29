import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import GuestApp from './pages/GuestApp'
import DJDashboard from './pages/DJDashboard'
import AdminPanel from './pages/AdminPanel'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (token && storedUser) {
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const handleLogin = (userData, token) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('token', token)
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={user ? <Navigate to="/" /> : <LoginPage onLogin={handleLogin} />}
        />
        <Route
          path="/register"
          element={user ? <Navigate to="/" /> : <RegisterPage onRegister={handleLogin} />}
        />

        {user?.role === 'admin' && (
          <Route
            path="/admin"
            element={<AdminPanel user={user} onLogout={handleLogout} />}
          />
        )}

        {user?.role === 'dj' && (
          <Route
            path="/dj"
            element={<DJDashboard user={user} onLogout={handleLogout} />}
          />
        )}

        <Route
          path="/event/:eventId"
          element={<GuestApp />}
        />

        <Route
          path="/"
          element={user ? (
            user.role === 'admin' ? <Navigate to="/admin" /> : <Navigate to="/dj" />
          ) : (
            <Navigate to="/login" />
          )}
        />
      </Routes>
    </Router>
  )
}

export default App
