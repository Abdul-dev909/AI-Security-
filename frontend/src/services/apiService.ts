import api from '../api/api.js'

/**
 * Checks the health status of the backend API.
 * @returns {Promise<any>} The response data.
 */
export async function checkHealth() {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    console.error('Error checking backend health:', error)
    throw error
  }
}

/**
 * Sends a chat message to the backend.
 * @param {string} message - The message text.
 * @returns {Promise<any>} The response data containing the assistant's reply.
 */
export async function sendChat(message: string) {
  try {
    const response = await api.post('/chat', { message })
    return response.data
  } catch (error) {
    console.error('Error sending chat message to backend:', error)
    throw error
  }
}
