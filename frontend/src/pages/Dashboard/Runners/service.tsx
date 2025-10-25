import {
  listInstancesRunnerGet,
  createInstanceRunnerPost,
  deleteInstanceRunnerInstanceIdDelete,
  startInstanceRunnerInstanceIdStartPost,
  stopInstanceRunnerInstanceIdStopPost,
  restartInstanceRunnerInstanceIdRestartPost,
  clearInstanceLogsRunnerInstanceIdLogsClearPost,
  cloneInstanceRunnerInstanceIdClonePost,
} from "@/lib/api"
import type { RunnerInstanceOut } from "@/lib/api"

export type CreateRunnerFormData = {
  runner_name: string
  github_url: string
  token: string
  labels: string
}

export async function listRunnersApi() {
  try {
    const response = await listInstancesRunnerGet({})

    if (response.data && Array.isArray(response.data)) {
      return { success: true, data: response.data as RunnerInstanceOut[] }
    }

    return { success: false, message: (response as any)?.error?.detail || "Failed to fetch runners", data: [] }
  } catch (error: any) {
    
    const detail = error?.detail || "Failed to fetch runners"
    return { success: false, message: detail, data: [] }
  }
}

export async function createRunnerApi({
  runner_name,
  github_url,
  token,
  labels,
}: CreateRunnerFormData) {
  try {
    const response = await createInstanceRunnerPost({
      body: {
        runner_name,
        github_url,
        token,
        labels,
      },
    })

    if (response.data) {
      return { success: true, data: response.data as RunnerInstanceOut }
    }

    return { success: false, message: response.error?.detail || "Failed to create runner" }
  } catch (error: any) {
    const detail = error?.message || "Failed to create runner"
    return { success: false, message: detail }
  }
}

export async function deleteRunnerApi(instance_id: number) {
  try {
    const response = await deleteInstanceRunnerInstanceIdDelete({
      path: {
        instance_id,
      },
    })

    if (response.data || !response.error) {
      return { success: true, message: "Runner deleted successfully" }
    }

    return { success: false, message: response.error?.detail || "Failed to delete runner" }
  } catch (error: any) {
    const detail = error?.message || "Failed to delete runner"
    return { success: false, message: detail }
  }
}

export async function startRunnerApi(instance_id: number) {
  try {
    const response = await startInstanceRunnerInstanceIdStartPost({
      path: {
        instance_id,
      },
    })

    if (response.data) {
      return { success: true, data: response.data as RunnerInstanceOut }
    }

    return { success: false, message: response.error?.detail || "Failed to start runner" }
  } catch (error: any) {
    const detail = error?.message || "Failed to start runner"
    return { success: false, message: detail }
  }
}

export async function stopRunnerApi(instance_id: number) {
  try {
    const response = await stopInstanceRunnerInstanceIdStopPost({
      path: {
        instance_id,
      },
    })

    if (response.data) {
      return { success: true, data: response.data as RunnerInstanceOut }
    }

    return { success: false, message: response.error?.detail || "Failed to stop runner" }
  } catch (error: any) {
    const detail = error?.message || "Failed to stop runner"
    return { success: false, message: detail }
  }
}

export async function restartRunnerApi(instance_id: number) {
  try {
    const response = await restartInstanceRunnerInstanceIdRestartPost({
      path: {
        instance_id,
      },
    })

    if (response.data) {
      return { success: true, data: response.data as RunnerInstanceOut }
    }

    return { success: false, message: response.error?.detail || "Failed to restart runner" }
  } catch (error: any) {
    const detail = error?.message || "Failed to restart runner"
    return { success: false, message: detail }
  }
}

export async function* getRunnerLogsApi(instance_id: number, signal?: AbortSignal) {
  try {
    // Get auth token from localStorage
    const token = localStorage.getItem("access_token")
    if (!token) {
      yield {
        status: "error",
        message: "Authentication token not found"
      }
      return
    }

    // Fetch directly from the API endpoint for real-time streaming
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
    const response = await fetch(`${baseUrl}/runner/${instance_id}/logs`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/x-ndjson",
      },
      signal: signal,
    })

    if (!response.ok) {
      yield {
        status: "error",
        message: `Failed to fetch logs: HTTP ${response.status}`
      }
      return
    }

    const reader = response.body?.getReader()
    if (!reader) {
      yield {
        status: "error",
        message: "Failed to get response reader"
      }
      return
    }

    const decoder = new TextDecoder()
    let buffer = ""

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || ""

        for (const line of lines) {
          if (line.trim()) {
            try {
              const parsed = JSON.parse(line)
              yield parsed
            } catch {
              // If not JSON, treat as plain log line
              yield { status: "streaming", log: line }
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  } catch (error: any) {
    // Don't yield error if aborted (user closed modal)
    if (error.name !== "AbortError") {
      yield {
        status: "error",
        message: error?.message || "Failed to fetch logs"
      }
    }
  }
}

export async function clearRunnerLogsApi(instance_id: number) {
  try {
    const response = await clearInstanceLogsRunnerInstanceIdLogsClearPost({
      path: {
        instance_id,
      },
    })

    if (response.data || !response.error) {
      return { success: true, message: "Logs cleared successfully" }
    }

    return { success: false, message: response.error?.detail || "Failed to clear logs" }
  } catch (error: any) {
    const detail = error?.message || "Failed to clear logs"
    return { success: false, message: detail }
  }
}

export async function cloneRunnerApi(instance_id: number, count: number, token?: string) {
  try {
    const response = await cloneInstanceRunnerInstanceIdClonePost({
      path: {
        instance_id,
      },
      body: {
        count,
        token: token || undefined,
      },
    })

    if (response.data) {
      return { success: true, data: response.data, message: "Runner cloned successfully" }
    }

    return { success: false, message: response.error?.detail || "Failed to clone runner" }
  } catch (error: any) {
    const detail = error?.message || "Failed to clone runner"
    return { success: false, message: detail }
  }
}
