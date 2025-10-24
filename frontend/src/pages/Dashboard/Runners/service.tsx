import {
  listInstancesRunnerGet,
  createInstanceRunnerPost,
  deleteInstanceRunnerInstanceIdDelete,
  startInstanceRunnerInstanceIdStartPost,
  stopInstanceRunnerInstanceIdStopPost,
  restartInstanceRunnerInstanceIdRestartPost,
} from "@/lib/api"
import type { RunnerInstanceOut } from "@/lib/api"
import type { CreateRunnerFormData } from "./CreateRunnerDialog"

export async function listRunnersApi() {
  try {
    const response = await listInstancesRunnerGet({})

    if (response.data && Array.isArray(response.data)) {
      return { success: true, data: response.data as RunnerInstanceOut[] }
    }

    return { success: false, message: "Failed to fetch runners", data: [] }
  } catch (error: any) {
    const detail = error?.message || "Failed to fetch runners"
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

    return { success: false, message: "Failed to create runner" }
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

    return { success: false, message: "Failed to delete runner" }
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

    return { success: false, message: "Failed to start runner" }
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

    return { success: false, message: "Failed to stop runner" }
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

    return { success: false, message: "Failed to restart runner" }
  } catch (error: any) {
    const detail = error?.message || "Failed to restart runner"
    return { success: false, message: detail }
  }
}
