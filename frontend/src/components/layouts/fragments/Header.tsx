"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Grid3x3, LogOut, HelpCircle, Moon, Sun, CheckIcon, ChevronsUpDownIcon, Server } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import { cn } from "@/lib/utils"
import { useTheme } from "@/components/providers/ThemeProvider"

export default function Header() {
  const { theme, setTheme } = useTheme()
  const { profile, logout } = useAuth()
  const email = profile?.email || ""
  const firstName = profile?.first_name || ""
  const lastName = profile?.last_name || ""

  const fallback =
    firstName && lastName
      ? `${firstName[0]}${lastName[0]}`.toUpperCase()
      : email
      ? email[0].toUpperCase()
      : "U"

  // Workspace data
  const workspaces = [
    { value: "workspace_a", label: "Workspace A" },
    { value: "workspace_b", label: "Workspace B" },
    { value: "workspace_c", label: "Workspace C" },
  ]
  const [selectedWorkspace, setSelectedWorkspace] = React.useState(workspaces[0].value)
  const [workspacePopoverOpen, setWorkspacePopoverOpen] = React.useState(false)

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
          

          {/* Workspace Combobox */}
          <Popover open={workspacePopoverOpen} onOpenChange={setWorkspacePopoverOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                role="combobox"
                aria-expanded={workspacePopoverOpen}
                className="w-[180px] justify-between text-sm"
              >
                {workspaces.find((ws) => ws.value === selectedWorkspace)?.label}
                <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[180px] p-0">
              <Command>
                <CommandInput placeholder="Search workspace..." />
                <CommandList>
                  <CommandEmpty>No workspace found.</CommandEmpty>
                  <CommandGroup>
                    {workspaces.map((ws) => (
                      <CommandItem
                        key={ws.value}
                        value={ws.value}
                        onSelect={(currentValue) => {
                          setSelectedWorkspace(currentValue)
                          setWorkspacePopoverOpen(false)
                        }}
                      >
                        <CheckIcon
                          className={cn(
                            "mr-2 h-4 w-4",
                            selectedWorkspace === ws.value ? "opacity-100" : "opacity-0"
                          )}
                        />
                        {ws.label}
                      </CommandItem>
                    ))}
                    <CommandItem
                      onSelect={() => {
                        console.log("Add workspace clicked")
                        setWorkspacePopoverOpen(false)
                      }}
                      className="text-blue-500"
                    >
                      + Add Workspace
                    </CommandItem>
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>

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
