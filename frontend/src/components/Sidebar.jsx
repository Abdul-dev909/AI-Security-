import { Link } from 'react-router-dom'

function Sidebar() {
  return (
    <nav>
      <Link to="/">Dashboard</Link>
      <Link to="/chat">Chat</Link>
    </nav>
  )
}

export default Sidebar
