import { useState } from 'react'

function AdminPanel({ user, onLogout }) {
  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Admin Panel</h1>
        <button
          onClick={onLogout}
          style={{
            padding: '10px 20px',
            backgroundColor: '#FF6B35',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Logout
        </button>
      </div>
      <p>Willkommen, {user?.email}</p>
      {/* Phase 5: Wird implementiert */}
      <div style={{ backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '4px' }}>
        <p>Phase 5: Admin-Panel-Implementierung (Wochen 12-13)</p>
      </div>
    </div>
  )
}

export default AdminPanel
