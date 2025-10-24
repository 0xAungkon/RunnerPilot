"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { createRunnerApi } from "./service"

interface AddRunnerModalProps {
  open: boolean
  onOpenChange: (v: boolean) => void
  onSuccess?: () => void
}

export default function AddRunnerModal({ open, onOpenChange, onSuccess }: AddRunnerModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    runner_name: "",
    github_url: "",
    token: "",
    labels: "",
  })
  const [error, setError] = useState("")

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async () => {
    setError("")

    // Validate form
    if (!formData.runner_name.trim()) {
      setError("Runner name is required")
      return
    }
    if (!formData.github_url.trim()) {
      setError("GitHub URL is required")
      return
    }
    if (!formData.token.trim()) {
      setError("Access token is required")
      return
    }

    setIsLoading(true)
    const result = await createRunnerApi({
      runner_name: formData.runner_name,
      github_url: formData.github_url,
      token: formData.token,
      labels: formData.labels,
    })

    if (result.success) {
      // Reset form
      setFormData({
        runner_name: "",
        github_url: "",
        token: "",
        labels: "",
      })
      onOpenChange(false)
      onSuccess?.()
    } else {
      setError(result.message || "Failed to create runner")
    }
    setIsLoading(false)
  }

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      // Reset form when closing
      setFormData({
        runner_name: "",
        github_url: "",
        token: "",
        labels: "",
      })
      setError("")
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md" style={{ maxWidth: 600 }}>
        <DialogHeader>
          <DialogTitle>Add New Runner</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-1">
            <Label>Runner Name</Label>
            <Input
              name="runner_name"
              placeholder="e.g. production-runner-1"
              value={formData.runner_name}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </div>

          <div className="space-y-1">
            <Label>GitHub Repository URL</Label>
            <Input
              name="github_url"
              placeholder="https://github.com/username/repo"
              value={formData.github_url}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </div>

          <div className="space-y-1">
            <Label>Access Token</Label>
            <Input
              name="token"
              placeholder="Enter GitHub PAT (Personal Access Token)"
              type="password"
              value={formData.token}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </div>

          <div className="space-y-1">
            <Label>Labels</Label>
            <Input
              name="labels"
              placeholder="Enter multiple labels separated by commas"
              value={formData.labels}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? "Adding..." : "Add Runner"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
