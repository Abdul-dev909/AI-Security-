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

/**
 * Fetches all registered attacks.
 */
export async function listAttacks() {
  try {
    const response = await api.get('/api/attacks')
    return response.data
  } catch (error) {
    console.error('Error listing attacks:', error)
    throw error
  }
}

/**
 * Runs a single attack by its ID.
 * @param {string} attackId - The ID of the attack to run.
 */
export async function runAttack(attackId: string) {
  try {
    const response = await api.post('/api/attacks/run', { attack_id: attackId })
    return response.data
  } catch (error) {
    console.error(`Error running attack ${attackId}:`, error)
    throw error
  }
}

/**
 * Runs all enabled attacks in batch.
 */
export async function runAllAttacks() {
  try {
    const response = await api.post('/api/attacks/run-all')
    return response.data
  } catch (error) {
    console.error('Error running all attacks:', error)
    throw error
  }
}
