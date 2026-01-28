import { useAuthStore } from '../stores/authStore'

type MessageHandler = (data: any) => void

class WebSocketService {
  private socket: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map()
  private pingInterval: NodeJS.Timeout | null = null

  connect() {
    const token = useAuthStore.getState().token
    if (!token) {
      console.log('No token available, skipping WebSocket connection')
      return
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.VITE_WS_URL || `${wsProtocol}//${window.location.host}`
    const wsUrl = `${wsHost}/api/v1/ws/notifications?token=${token}`

    try {
      this.socket = new WebSocket(wsUrl)

      this.socket.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.startPing()
      }

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        this.stopPing()
        this.attemptReconnect()
      }

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }

  disconnect() {
    this.stopPing()
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    this.reconnectAttempts = this.maxReconnectAttempts // Prevent reconnection
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)

    setTimeout(() => {
      this.connect()
    }, this.reconnectDelay * this.reconnectAttempts)
  }

  private startPing() {
    this.pingInterval = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.send({ action: 'ping', timestamp: Date.now() })
      }
    }, 30000) // Ping every 30 seconds
  }

  private stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  send(data: any) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data))
    }
  }

  subscribe(room: string) {
    this.send({ action: 'subscribe', room })
  }

  unsubscribe(room: string) {
    this.send({ action: 'unsubscribe', room })
  }

  private handleMessage(data: any) {
    const { type } = data
    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      handlers.forEach((handler) => handler(data))
    }

    // Also notify 'all' handlers
    const allHandlers = this.messageHandlers.get('all')
    if (allHandlers) {
      allHandlers.forEach((handler) => handler(data))
    }
  }

  on(type: string, handler: MessageHandler) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set())
    }
    this.messageHandlers.get(type)!.add(handler)

    // Return unsubscribe function
    return () => {
      this.messageHandlers.get(type)?.delete(handler)
    }
  }

  off(type: string, handler: MessageHandler) {
    this.messageHandlers.get(type)?.delete(handler)
  }
}

export const wsService = new WebSocketService()
