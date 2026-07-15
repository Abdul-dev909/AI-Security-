import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar.jsx'
import Navbar from '../components/Navbar.jsx'

function MainLayout() {
  return (
    <div>
      <Navbar />
      <div>
        <Sidebar />
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default MainLayout
