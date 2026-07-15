import { Routes, Route } from 'react-router-dom'
import MainLayout from '../layouts/MainLayout.jsx'
import Dashboard from '../pages/Dashboard.jsx'
import Chat from '../pages/Chat.jsx'
import NotFound from '../pages/NotFound.jsx'

function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/chat" element={<Chat />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default AppRoutes
