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
  const [errors, setErrors] = useState({
    runner_name: "",
    github_url: "",
    token: "",
    labels: "",
  })

  // Validation functions
  const validateRunnerName = (value: string): string => {
    if (!value.trim()) {
      return "Runner name is required"
    }
    if (!/^[a-z0-9-]+$/.test(value)) {
      return "Only lowercase letters, numbers, and hyphens are allowed"
    }
    if (value.startsWith("-") || value.endsWith("-")) {
      return "Runner name cannot start or end with a hyphen"
    }
    return ""
  }

  const validateGithubUrl = (value: string): string => {
    if (!value.trim()) {
      return "GitHub URL is required"
    }
    const githubUrlRegex = /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/
    if (!githubUrlRegex.test(value)) {
      return "Please enter a valid GitHub URL (e.g., https://github.com/username/repo)"
    }
    return ""
  }

  const validateToken = (value: string): string => {
    if (!value.trim()) {
      return "Access token is required"
    }
    return ""
  }

  const validateLabels = (value: string): string => {
    if (!value.trim()) {
      return ""
    }
    if (value.includes(" ")) {
      return "Labels cannot contain spaces. Use commas to separate labels"
    }
    return ""
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    let processedValue = value

    // Auto-convert runner name to lowercase with hyphens
    if (name === "runner_name") {
      processedValue = value.toLowerCase().replace(/\s+/g, "-")
    }

    setFormData((prev) => ({
      ...prev,
      [name]: processedValue,
    }))

    // Real-time validation
    let error = ""
    if (name === "runner_name") {
      error = validateRunnerName(processedValue)
    } else if (name === "github_url") {
      error = validateGithubUrl(processedValue)
    } else if (name === "token") {
      error = validateToken(processedValue)
    } else if (name === "labels") {
      error = validateLabels(processedValue)
    }

    setErrors((prev) => ({
      ...prev,
      [name]: error,
    }))
  }

  const handleSubmit = async () => {
    // Validate all fields
    const newErrors = {
      runner_name: validateRunnerName(formData.runner_name),
      github_url: validateGithubUrl(formData.github_url),
      token: validateToken(formData.token),
      labels: validateLabels(formData.labels),
    }

    setErrors(newErrors)

    // Check if there are any errors
    const hasErrors = Object.values(newErrors).some((error) => error !== "")
    if (hasErrors) {
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
      setErrors({
        runner_name: "",
        github_url: "",
        token: "",
        labels: "",
      })
      onOpenChange(false)
      onSuccess?.()
    } else {
      setErrors((prev) => ({
        ...prev,
        runner_name: result.message || "Failed to create runner",
      }))
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
      setErrors({
        runner_name: "",
        github_url: "",
        token: "",
        labels: "",
      })
    }
    onOpenChange(newOpen)
  }

  // Check if form is valid
  const isFormValid = Object.values(errors).every((error) => error === "") &&
    Object.values(formData).some((value) => value.trim() !== "")

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md" style={{ maxWidth: 600 }}>
        <DialogHeader>
          <DialogTitle>Add New Runner</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-1">
            <Label>Runner Name</Label>
            <Input
              name="runner_name"
              placeholder="e.g. production-runner-1"
              value={formData.runner_name}
              onChange={handleInputChange}
              disabled={isLoading}
              className={errors.runner_name ? "border-red-500" : ""}
            />
            {errors.runner_name && (
              <p className="text-red-500 text-sm">{errors.runner_name}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label>GitHub Repository URL</Label>
            <Input
              name="github_url"
              placeholder="https://github.com/username/repo"
              value={formData.github_url}
              onChange={handleInputChange}
              disabled={isLoading}
              className={errors.github_url ? "border-red-500" : ""}
            />
            {errors.github_url && (
              <p className="text-red-500 text-sm">{errors.github_url}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label>Access Token</Label>
            <Input
              name="token"
              placeholder="Enter GitHub Runner Token"
              type="password"
              value={formData.token}
              onChange={handleInputChange}
              disabled={isLoading}
              className={errors.token ? "border-red-500" : ""}
            />
            {errors.token && (
              <p className="text-red-500 text-sm">{errors.token}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label>Labels</Label>
            <Input
              name="labels"
              placeholder="Enter multiple labels separated by commas"
              value={formData.labels}
              onChange={handleInputChange}
              disabled={isLoading}
              className={errors.labels ? "border-red-500" : ""}
            />
            {errors.labels && (
              <p className="text-red-500 text-sm">{errors.labels}</p>
            )}
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
          <Button onClick={handleSubmit} disabled={isLoading || !isFormValid}>
            {isLoading ? "Adding..." : "Add Runner"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
