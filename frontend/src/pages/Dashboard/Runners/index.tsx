"use client"

import { useEffect, useState, useMemo } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Filter, Download, Plus } from "lucide-react"
import { toast } from "sonner"
import type { RunnerInstanceOut } from "@/lib/api"
import {
  listRunnersApi,
  createRunnerApi,
  updateRunnerApi,
  deleteRunnerApi,
  startRunnerApi,
  stopRunnerApi,
  restartRunnerApi,
} from "./service"
import { CreateRunnerDialog, type CreateRunnerFormData } from "./CreateRunnerDialog"
import { RunnerActions } from "./RunnerActions"

export default function RunnersPage() {
  const [runners, setRunners] = useState<RunnerInstanceOut[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editingRunner, setEditingRunner] = useState<RunnerInstanceOut | null>(null)

  // Fetch runners on mount
  useEffect(() => {
    fetchRunners()
  }, [])

  const fetchRunners = async () => {
    setLoading(true)
    try {
      const result = await listRunnersApi()
      if (result.success) {
        setRunners(result.data)
      } else {
        toast.error(result.message)
      }
    } finally {
      setLoading(false)
    }
  }

  // Filter and search runners
  const filteredRunners = useMemo(() => {
    return runners.filter((runner) => {
      const matchesSearch =
        runner.runner_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        runner.github_url.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (runner.labels?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false)

      const matchesStatus =
        statusFilter === "all" || runner.status.toLowerCase() === statusFilter.toLowerCase()

      return matchesSearch && matchesStatus
    })
  }, [runners, searchQuery, statusFilter])

  const handleCreateRunner = async (data: CreateRunnerFormData) => {
    setActionLoading(true)
    try {
      const result = await createRunnerApi(data)
      if (result.success) {
        toast.success("Runner created successfully!")
        setRunners([...runners, result.data])
        setCreateDialogOpen(false)
      } else {
        toast.error(result.message)
      }
    } finally {
      setActionLoading(false)
    }
  }

  const handleUpdateRunner = async (data: CreateRunnerFormData) => {
    if (!editingRunner) return

    setActionLoading(true)
    try {
      const result = await updateRunnerApi({
        instance_id: editingRunner.id,
        token: data.token,
      })
      if (result.success) {
        toast.success("Runner updated successfully!")
        setRunners(runners.map((r) => (r.id === editingRunner.id ? result.data : r)))
        setEditingRunner(null)
        setCreateDialogOpen(false)
      } else {
        toast.error(result.message)
      }
    } finally {
      setActionLoading(false)
    }
  }

  const handleStartRunner = async (instanceId: number) => {
    setActionLoading(true)
    try {
      const result = await startRunnerApi(instanceId)
      if (result.success) {
        toast.success("Runner started successfully!")
        setRunners(runners.map((r) => (r.id === instanceId ? result.data : r)))
      } else {
        toast.error(result.message)
      }
    } finally {
      setActionLoading(false)
    }
  }

  const handleStopRunner = async (instanceId: number) => {
    setActionLoading(true)
    try {
      const result = await stopRunnerApi(instanceId)
      if (result.success) {
        toast.success("Runner stopped successfully!")
        setRunners(runners.map((r) => (r.id === instanceId ? result.data : r)))
      } else {
        toast.error(result.message)
      }
    } finally {
      setActionLoading(false)
    }
  }

  const handleRestartRunner = async (instanceId: number) => {
    setActionLoading(true)
    try {
      const result = await restartRunnerApi(instanceId)
      if (result.success) {
        toast.success("Runner restarted successfully!")
        setRunners(runners.map((r) => (r.id === instanceId ? result.data : r)))
      } else {
        toast.error(result.message)
      }
    } finally {
      setActionLoading(false)
    }
  }

  const handleDeleteRunner = async (instanceId: number) => {
    if (!window.confirm("Are you sure you want to delete this runner? This action cannot be undone.")) {
      return
    }

    setActionLoading(true)
    try {
      const result = await deleteRunnerApi(instanceId)
      if (result.success) {
        toast.success("Runner deleted successfully!")
        setRunners(runners.filter((r) => r.id !== instanceId))
      } else {
        toast.error(result.message)
      }
    } finally {
      setActionLoading(false)
    }
  }

  const handleEditRunner = (runner: RunnerInstanceOut) => {
    setEditingRunner(runner)
    setCreateDialogOpen(true)
  }

  const handleCreateDialogClose = (open: boolean) => {
    setCreateDialogOpen(open)
    if (!open) {
      setEditingRunner(null)
    }
  }

  const handleSubmitDialog = editingRunner ? handleUpdateRunner : handleCreateRunner

  return (
    <div className="min-h-screen bg-background text-foreground p-6">
      <CreateRunnerDialog
        open={createDialogOpen}
        onOpenChange={handleCreateDialogClose}
        onSubmit={handleSubmitDialog}
        runner={editingRunner}
        loading={actionLoading}
      />

      {/* Toolbar */}
      <div className="flex justify-between items-center mb-5">
        <div className="flex-1 mr-4">
          <Input
            placeholder="Search by name, URL, or labels..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 text-sm bg-muted text-foreground border border-border"
          />
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 px-2 py-1 border border-border rounded-md bg-muted">
            <Filter className="w-3.5 h-3.5 text-muted-foreground" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs bg-muted text-foreground border-0 outline-none cursor-pointer"
            >
              <option value="all">All Status</option>
              <option value="online">Online</option>
              <option value="offline">Offline</option>
            </select>
          </div>
          <Button variant="outline" size="icon" className="h-8 w-8">
            <Download className="w-3.5 h-3.5" />
          </Button>
          <Button
            className="h-8 px-3 text-xs gap-1"
            onClick={() => {
              setEditingRunner(null)
              setCreateDialogOpen(true)
            }}
          >
            <Plus className="w-3.5 h-3.5" />
            Add Runner
          </Button>
        </div>
      </div>

      {/* List Header */}
      <div className="grid grid-cols-[1.5fr_1.5fr_1fr_1.2fr_0.6fr] text-xs font-medium text-muted-foreground border-b border-border pb-2 mb-1">
        <div>Name</div>
        <div>GitHub URL</div>
        <div>Labels</div>
        <div>Status / Created</div>
        <div className="text-right pr-2">Actions</div>
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border border-muted-foreground border-t-foreground" />
        </div>
      ) : filteredRunners.length === 0 ? (
        <div className="flex justify-center items-center py-12">
          <div className="text-center">
            <p className="text-muted-foreground mb-4">
              {runners.length === 0 ? "No runners yet" : "No runners match your search"}
            </p>
            {runners.length === 0 && (
              <Button
                onClick={() => {
                  setEditingRunner(null)
                  setCreateDialogOpen(true)
                }}
              >
                <Plus className="w-3.5 h-3.5 mr-2" />
                Create Your First Runner
              </Button>
            )}
          </div>
        </div>
      ) : (
        /* Runner Rows */
        <div className="divide-y divide-border text-xs">
          {filteredRunners.map((runner, idx) => (
            <motion.div
              key={runner.id}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: idx * 0.04 }}
              className="grid grid-cols-[1.5fr_1.5fr_1fr_1.2fr_0.6fr] items-center py-2.5 hover:bg-muted/40 transition-colors"
            >
              {/* Name */}
              <div>
                <div className="font-medium text-foreground truncate capitalize">
                  {runner.runner_name}
                </div>
                <div className="text-muted-foreground truncate text-[10px] mt-1">
                  ID: {runner.id}
                </div>
              </div>

              {/* GitHub URL */}
              <div className="truncate text-muted-foreground">
                <a href={runner.github_url} target="_blank" rel="noopener noreferrer" className="hover:underline text-blue-500">
                  {runner.github_url.replace("https://", "").slice(0, 40)}...
                </a>
              </div>

              {/* Labels */}
              <div className="flex flex-wrap gap-1">
                {runner.labels ? (
                  runner.labels.split(",").map((label) => (
                    <Badge key={label} variant="secondary" className="text-[10px] px-2 py-0">
                      {label.trim()}
                    </Badge>
                  ))
                ) : (
                  <span className="text-muted-foreground">-</span>
                )}
              </div>

              {/* Status + Created */}
              <div className="flex items-center gap-2">
                <span
                  className={`inline-block w-2 h-2 rounded-full ${
                    runner.status.toLowerCase() === "online"
                      ? "bg-green-500"
                      : "bg-muted-foreground"
                  }`}
                />
                <div>
                  <div className="capitalize">{runner.status}</div>
                  <div className="text-muted-foreground text-[10px] mt-0.5">
                    {new Date(runner.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="text-right pr-2">
                <RunnerActions
                  runner={runner}
                  onStart={handleStartRunner}
                  onStop={handleStopRunner}
                  onRestart={handleRestartRunner}
                  onEdit={handleEditRunner}
                  onDelete={handleDeleteRunner}
                  loading={actionLoading}
                />
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
