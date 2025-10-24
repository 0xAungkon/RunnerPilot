"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Download,
  Plus,
  MoreVertical,
  ChevronDown,
  Link2Icon
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"

import AddRunnerModal from "./AddRunnerModal"
import CloneRunnerModal from "./CloneRunnerModal"
import { listRunnersApi, startRunnerApi, stopRunnerApi, restartRunnerApi } from "./service"

export default function MachineList() {
  const [statusFilter, setStatusFilter] = useState("All")
  const [searchQuery, setSearchQuery] = useState("")
  const [openAdd, setOpenAdd] = useState(false)
  const [openClone, setOpenClone] = useState(false)
  const [machines, setMachines] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastActivity, setLastActivity] = useState(Date.now())
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const table_column_grid_template = "2fr_1.4fr_1.5fr_0.5fr_1.5fr_0.4fr_0.2fr"

  const fetchRunners = async () => {
    setIsLoading(true)
    const result = await listRunnersApi()
    if (result.success) {
      setMachines(result.data)
    }
    setIsLoading(false)
  }

  const handleStartRunner = async (instance_id: number) => {
    setActionLoading(instance_id)
    const result = await startRunnerApi(instance_id)
    if (result.success) {
      await fetchRunners()
      setLastActivity(Date.now())
    }
    setActionLoading(null)
  }

  const handleStopRunner = async (instance_id: number) => {
    setActionLoading(instance_id)
    const result = await stopRunnerApi(instance_id)
    if (result.success) {
      await fetchRunners()
      setLastActivity(Date.now())
    }
    setActionLoading(null)
  }

  const handleRestartRunner = async (instance_id: number) => {
    setActionLoading(instance_id)
    const result = await restartRunnerApi(instance_id)
    if (result.success) {
      await fetchRunners()
      setLastActivity(Date.now())
    }
    setActionLoading(null)
  }

  // Initial fetch
  useEffect(() => {
    fetchRunners()
  }, [])

  // Auto-refresh every 1 minute if no user activity
  useEffect(() => {
    const handleUserActivity = () => {
      setLastActivity(Date.now())
    }

    // Add event listeners for user activity
    window.addEventListener("click", handleUserActivity)
    window.addEventListener("keydown", handleUserActivity)
    window.addEventListener("mousemove", handleUserActivity)

    // Set up auto-refresh interval
    const refreshInterval = setInterval(() => {
      const now = Date.now()
      const inactiveSeconds = (now - lastActivity) / 1000
      
      // Refresh if user has been inactive for 60 seconds
      if (inactiveSeconds >= 60) {
        fetchRunners()
        setLastActivity(now)
      }
    }, 5000) // Check every 5 seconds

    return () => {
      window.removeEventListener("click", handleUserActivity)
      window.removeEventListener("keydown", handleUserActivity)
      window.removeEventListener("mousemove", handleUserActivity)
      clearInterval(refreshInterval)
    }
  }, [lastActivity])

  const filteredMachines = machines.filter((machine) => {
    const matchesSearch = machine.runner_name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === "All" || machine.status.toLowerCase() === statusFilter.toLowerCase()
    return matchesSearch && matchesStatus
  })
  return (
    <div className="min-h-screen bg-background text-foreground p-6">
      {/* Toolbar */}
      <div className="flex justify-between items-center mb-5">
        <div className="w-1/2">
          <Input
            placeholder="Search by name, owner, tag, version..."
            className="h-8 text-sm bg-muted text-foreground border border-border"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Status Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="h-8 px-3 text-xs gap-1">
                Status: {statusFilter} <ChevronDown className="w-3.5 h-3.5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {["All", "Active", "Stopped", "Error"].map((status) => (
                <DropdownMenuItem
                  key={status}
                  onClick={() => setStatusFilter(status)}
                >
                  {status}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          
          <Button
            className="h-8 px-3 text-xs gap-1"
            onClick={() => setOpenAdd(true)}
          >
            <Plus className="w-3.5 h-3.5" />
            Add
          </Button>
        </div>
      </div>

      {/* List Header */}
     <div className={`grid grid-cols-[${table_column_grid_template}] text-xs font-medium text-muted-foreground border-b border-border pb-2 mb-1`}>
  <div>Runner</div>
  <div>Hostname</div>
  <div>Token</div>
  <div>Last Seen</div>
  <div className="mx-auto">Status</div>
  <div className="text-right pr-2">Actions</div>
</div>

      {/* Machine Rows */}
<div className="divide-y divide-border text-xs ">
  {isLoading ? (
    <div className="py-8 text-center text-muted-foreground">Loading runners...</div>
  ) : filteredMachines.length === 0 ? (
    <div className="py-8 text-center text-muted-foreground">No runners found</div>
  ) : (
    filteredMachines.map((machine, idx) => (
    <motion.div
      key={idx}
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: idx * 0.04 }}
      className={`grid grid-cols-[${table_column_grid_template}] items-center py-2.5 hover:bg-muted/40 transition-colors`}
    >
      {/* Runner Name + Hostname + Labels */}
      <div >
        <div className="font-medium text-foreground truncate text-lg capitalize flex items-center gap-2">
          {machine.runner_name.replace(/-/g, " ")}
          <a
            href={machine.github_url}
            target="_blank"
            rel="noopener noreferrer"
            title={machine.github_url}
            className="text-muted-foreground hover:text-blue-500"
          >
            <Link2Icon className="w-4 h-4" />
          </a>
        </div>
        <div className="flex flex-wrap gap-1 mt-2">
        {machine.labels.split(",").map((label: string, i: number) => (
          <Badge key={i} variant="secondary" className="text-[10px] px-2 py-0">
            {label.trim()}
          </Badge>
        ))}
      </div>
      </div>

      {/* GitHub URL */}
      <div className="truncate">
            {machine.hostname ? (
              <span
                title={machine.hostname}
                onClick={() => navigator.clipboard.writeText(machine.hostname)}
                className="cursor-pointer"
              >
                {machine.hostname.length > 12
                  ? machine.hostname.slice(0, 12) + "…"
                  : machine.hostname}
              </span>
            ) : (
              <span className="text-muted-foreground italic">N/A</span>
            )}
      </div>

      <div className="truncate">
        <span
          className="cursor-pointer select-none"
          title="Click to copy"
          onClick={() => navigator.clipboard.writeText(machine.token)}
        >
          {machine.token.slice(0, 5)}
          {"*".repeat(machine.token.length - 5)}
        </span>
      </div>
      
      {/* Created At */}
      <div className="truncate">
        {(() => {
          const now = new Date();
          const created = new Date(machine.created_at);
          const diffMs = now.getTime() - created.getTime();
          const diffSec = Math.floor(diffMs / 1000);
          const diffMin = Math.floor(diffSec / 60);
          const diffHour = Math.floor(diffMin / 60);

          if (diffMin < 1) return "Just now";
          if (diffMin < 60) return `${diffMin} minute${diffMin === 1 ? "" : "s"} ago`;
          if (diffHour < 24) return `${diffHour} hour${diffHour === 1 ? "" : "s"} ago`;
          // If more than 1 hour, show date and time in human-friendly format
          return created.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
          });
        })()}
      </div>

      {/* Status */}
      <div className="flex items-center justify-center">
        <div className="mx-auto">
        <span
          className={`inline-block w-2 h-2 rounded-full mr-2 ${
        machine.status.toLowerCase() === "active"
          ? "bg-green-500"
          : machine.status.toLowerCase() === "stopped"
          ? "bg-red-500"
          : machine.status.toLowerCase() === "error"
          ? "bg-red-600"
          : "bg-yellow-500"
          }`}
        />
        <span className="capitalize">{machine.status}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end items-center pr-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <MoreVertical className="w-4 h-4 text-muted-foreground cursor-pointer" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem 
              onClick={() => handleStartRunner(machine.id)}
              disabled={actionLoading === machine.id}
            >
              {actionLoading === machine.id ? "Starting..." : "Start"}
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => handleStopRunner(machine.id)}
              disabled={actionLoading === machine.id}
            >
              {actionLoading === machine.id ? "Stopping..." : "Stop"}
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => handleRestartRunner(machine.id)}
              disabled={actionLoading === machine.id}
            >
              {actionLoading === machine.id ? "Restarting..." : "Restart"}
            </DropdownMenuItem>
            <DropdownMenuItem>Logs</DropdownMenuItem>
            <DropdownMenuItem>Delete</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setOpenClone(true)}>
              Clone
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </motion.div>
    ))
  )}
</div>

      {/* Modals */}
      <AddRunnerModal 
        open={openAdd} 
        onOpenChange={setOpenAdd}
        onSuccess={() => {
          fetchRunners()
          setLastActivity(Date.now())
        }}
      />
      <CloneRunnerModal open={openClone} onOpenChange={setOpenClone} />
    </div>
  )
}
