"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { LogOut, Moon, Sun, Server } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useTheme } from "@/components/providers/ThemeProvider"

export default function Header() {
  const { theme, setTheme } = useTheme()
  const { profile, logout } = useAuth()
  const email = profile?.sub || ""
  const firstName = profile?.first_name || ""
  const lastName = profile?.last_name || ""
  

  const fallback =
    firstName && lastName
      ? `${firstName[0]}${lastName[0]}`.toUpperCase()
      : email
      ? email[0].toUpperCase()
      : "U"

  return (
    <header className="border-b border-gray-800 px-6 py-3">
      <div className="flex items-center justify-between max-w-7xl mx-auto gap-3">
        {/* Left Side */}
        <div className="flex items-center gap-2">
          <Server className="h-5 w-5 text-blue-500" />
          <span className="text-lg font-semibold text-foreground">Runner Pilot</span>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-3">
          {/* Profile Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Avatar className="h-8 w-8 cursor-pointer">
                <AvatarImage src="/abstract-profile.png" />
                <AvatarFallback>{fallback}</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <div className="px-4 py-2 text-sm text-muted-foreground border-b border-gray-700">
                {email}
              </div>

              <DropdownMenuItem
                onClick={() => setTheme(theme === "light" ? "dark" : "light")}
                className="flex items-center gap-2 cursor-pointer"
              >
                {theme === "light" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                {theme === "light" ? "Light Mode" : "Dark Mode"}
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={logout}
                className="flex items-center gap-2 cursor-pointer"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
