/**
 * AuthContext.tsx
 * 
 * Provides authentication context for managing JWT-based login state,
 * token persistence, and user session validation across the application.
 * 
 * Best Practices Applied:
 * - Type safety with interfaces
 * - Token stored in localStorage for persistence
 * - Auto logout on token expiry
 * - Safe JWT decoding with error handling
 * - Clean separation of context, provider, and hook
 * 
 * - TODO:
 *  - Refresh token handling
 */

import { createContext, useContext, useEffect, useState, useCallback } from "react"
import { jwtDecode } from "jwt-decode"
import { meCommonMeGet } from "@/lib/api"

// --------------------
// Types & Interfaces
// --------------------
interface AuthContextType {
  user: any
  token: string | null
  login: (token: string) => void
  logout: () => void
  profile: any
  fetchProfile: () => Promise<any>
  getProfile: () => Promise<any>
}

// --------------------
// Context Initialization
// --------------------
const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
  profile: null,
  fetchProfile: async () => null,
  getProfile: async () => null,
})

// --------------------
// Auth Provider Component
// --------------------
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<any>(null)
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("access_token") || null
  )
  const [profile, setProfile] = useState<any>(null)

  /**
   * Effect: Decode and validate token whenever it changes
   */
  useEffect(() => {
    if (!token) return

    try {
      const decoded: any = jwtDecode(token)
      const currentTime = Date.now() / 1000

      if (decoded.exp && decoded.exp < currentTime) {
        logout()
      } else {
        setUser(decoded)
        // Try to load profile from localStorage or token
        loadProfile(decoded)
      }
    } catch (error) {
      console.error("Invalid token", error)
      logout()
    }
  }, [token])

  // Helper: Load profile from localStorage or token
  const loadProfile = useCallback((decoded: any) => {
    const cached = localStorage.getItem("user_profile")
    const cachedTime = localStorage.getItem("user_profile_time")
    let shouldFetch = true
    if (cached && cachedTime) {
      const age = Date.now() - parseInt(cachedTime, 10)
      if (age < 3600 * 1000) {
        setProfile(JSON.parse(cached))
        shouldFetch = false
      }
    }
    if (shouldFetch) {
      // fallback to token
      if (decoded?.user) {
        setProfile(decoded.user)
      }
      fetchProfile()
    }
  }, [])

  // Fetch profile from API, cache in localStorage
  const fetchProfile = useCallback(async () => {
    try {
      const response = await meCommonMeGet()
      setProfile(response.data)
      localStorage.setItem("user_profile", JSON.stringify(response.data))
      localStorage.setItem("user_profile_time", Date.now().toString())
      return response.data
    } catch (error) {
      // fallback to token user if available
      if (user?.user) {
        setProfile(user.user)
        return user.user
      }
      return null
    }
  }, [user])

  // Get profile, auto-refresh if older than 1hr
  const getProfile = useCallback(async () => {
    const cached = localStorage.getItem("user_profile")
    const cachedTime = localStorage.getItem("user_profile_time")
    if (cached && cachedTime) {
      const age = Date.now() - parseInt(cachedTime, 10)
      if (age < 3600 * 1000) {
        const parsed = JSON.parse(cached)
        setProfile(parsed)
        return parsed
      }
    }
    // If not found or too old, fetch and update everywhere
    const fresh = await fetchProfile()
    setProfile(fresh)
    return fresh
  }, [fetchProfile])

  /**
   * Stores token and updates user state
   */
  const login = (newToken: string) => {
    localStorage.setItem("access_token", newToken)
    setToken(newToken)
    // Reset profile cache on login
    localStorage.removeItem("user_profile")
    localStorage.removeItem("user_profile_time")
    setProfile(null)
  }

  /**
   * Clears token and resets authentication state
   */
  const logout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("user_profile")
    localStorage.removeItem("user_profile_time")
    setToken(null)
    setUser(null)
    setProfile(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, profile, fetchProfile, getProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

// --------------------
// Custom Hook
// --------------------
export const useAuth = () => useContext(AuthContext)
