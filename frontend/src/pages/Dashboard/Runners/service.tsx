import {
  listInstancesRunnerGet,

import React, { useEffect } from "react"  createInstanceRunnerPost,

import {  deleteInstanceRunnerInstanceIdDelete,

  Dialog,  updateInstanceRunnerInstanceIdPut,

  DialogContent,  startInstanceRunnerInstanceIdStartPost,

  DialogDescription,  stopInstanceRunnerInstanceIdStopPost,

  DialogHeader,  restartInstanceRunnerInstanceIdRestartPost,

  DialogTitle,} from "@/lib/api";

} from "@/components/ui/dialog"import type { RunnerInstanceOut } from "@/lib/api";

import { Button } from "@/components/ui/button"

import { Input } from "@/components/ui/input"export async function listRunnersApi() {

import { Label } from "@/components/ui/label"  try {

import { Spinner } from "@/components/ui/spinner"    const response = await listInstancesRunnerGet({});

import type { RunnerInstanceOut } from "@/lib/api"

    if (response.data && Array.isArray(response.data)) {

interface CreateRunnerDialogProps {      return { success: true, data: response.data as RunnerInstanceOut[] };

  open: boolean    }

  onOpenChange: (open: boolean) => void

  onSubmit: (data: CreateRunnerFormData) => Promise<void>    return { success: false, message: "Failed to fetch runners", data: [] };

  runner?: RunnerInstanceOut | null  } catch (error: any) {

  loading?: boolean    const detail = error?.message || "Failed to fetch runners";

}    return { success: false, message: detail, data: [] };

  }

export interface CreateRunnerFormData {}

  runner_name?: string

  github_url: stringexport async function createRunnerApi({

  token: string  runner_name,

  labels?: string  github_url,

}  token,

  labels,

export function CreateRunnerDialog({}: {

  open,  runner_name?: string;

  onOpenChange,  github_url: string;

  onSubmit,  token: string;

  runner,  labels?: string;

  loading = false,}) {

}: CreateRunnerDialogProps) {  try {

  const [form, setForm] = React.useState<CreateRunnerFormData>({    const response = await createInstanceRunnerPost({

    runner_name: "",      body: {

    github_url: "",        runner_name,

    token: "",        github_url,

    labels: "",        token,

  })        labels,

  const [submitting, setSubmitting] = React.useState(false)      },

    });

  useEffect(() => {

    if (runner) {    if (response.data) {

      setForm({      return { success: true, data: response.data as RunnerInstanceOut };

        runner_name: runner.runner_name || "",    }

        github_url: runner.github_url,

        token: runner.token,    return { success: false, message: "Failed to create runner" };

        labels: runner.labels || "",  } catch (error: any) {

      })    const detail = error?.message || "Failed to create runner";

    } else {    return { success: false, message: detail };

      setForm({  }

        runner_name: "",}

        github_url: "",

        token: "",export async function updateRunnerApi({

        labels: "",  instance_id,

      })  token,

    }}: {

  }, [runner, open])  instance_id: number;

  token: string;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {}) {

    setForm({ ...form, [e.target.name]: e.target.value })  try {

  }    const response = await updateInstanceRunnerInstanceIdPut({

      path: {

  const handleSubmit = async (e: React.FormEvent) => {        instance_id,

    e.preventDefault()      },

    setSubmitting(true)      body: {

    try {        token,

      await onSubmit(form)      },

      onOpenChange(false)    });

    } finally {

      setSubmitting(false)    if (response.data) {

    }      return { success: true, data: response.data as RunnerInstanceOut };

  }    }



  return (    return { success: false, message: "Failed to update runner" };

    <Dialog open={open} onOpenChange={onOpenChange}>  } catch (error: any) {

      <DialogContent className="sm:max-w-[425px]">    const detail = error?.message || "Failed to update runner";

        <DialogHeader>    return { success: false, message: detail };

          <DialogTitle>{runner ? "Update Runner" : "Create New Runner"}</DialogTitle>  }

          <DialogDescription>}

            {runner

              ? "Update the runner configuration. Token is required for updates."export async function deleteRunnerApi(instance_id: number) {

              : "Fill in the details to create a new GitHub runner instance."}  try {

          </DialogDescription>    const response = await deleteInstanceRunnerInstanceIdDelete({

        </DialogHeader>      path: {

        instance_id,

        <form onSubmit={handleSubmit} className="space-y-4">      },

          <div>    });

            <Label htmlFor="runner_name">Runner Name (Optional)</Label>

            <Input    if (response.data || !response.error) {

              id="runner_name"      return { success: true, message: "Runner deleted successfully" };

              name="runner_name"    }

              type="text"

              value={form.runner_name}    return { success: false, message: "Failed to delete runner" };

              onChange={handleChange}  } catch (error: any) {

              placeholder="e.g., my-runner"    const detail = error?.message || "Failed to delete runner";

              className="mt-2"    return { success: false, message: detail };

              disabled={submitting || loading}  }

            />}

            <p className="text-xs text-muted-foreground mt-1">

              Leave empty for auto-generated nameexport async function startRunnerApi(instance_id: number) {

            </p>  try {

          </div>    const response = await startInstanceRunnerInstanceIdStartPost({

      path: {

          <div>        instance_id,

            <Label htmlFor="github_url">GitHub Repository URL *</Label>      },

            <Input    });

              id="github_url"

              name="github_url"    if (response.data) {

              type="url"      return { success: true, data: response.data as RunnerInstanceOut };

              value={form.github_url}    }

              onChange={handleChange}

              placeholder="https://github.com/owner/repo"    return { success: false, message: "Failed to start runner" };

              className="mt-2"  } catch (error: any) {

              required    const detail = error?.message || "Failed to start runner";

              disabled={submitting || loading || !!runner}    return { success: false, message: detail };

            />  }

          </div>}



          <div>export async function stopRunnerApi(instance_id: number) {

            <Label htmlFor="token">GitHub Token *</Label>  try {

            <Input    const response = await stopInstanceRunnerInstanceIdStopPost({

              id="token"      path: {

              name="token"        instance_id,

              type="password"      },

              value={form.token}    });

              onChange={handleChange}

              placeholder="ghp_xxxxxxxxxxxx"    if (response.data) {

              className="mt-2"      return { success: true, data: response.data as RunnerInstanceOut };

              required    }

              disabled={submitting || loading}

            />    return { success: false, message: "Failed to stop runner" };

            <p className="text-xs text-muted-foreground mt-1">  } catch (error: any) {

              {runner    const detail = error?.message || "Failed to stop runner";

                ? "Enter a new token to update"    return { success: false, message: detail };

                : "Personal access token with repo and workflow access"}  }

            </p>}

          </div>

export async function restartRunnerApi(instance_id: number) {

          <div>  try {

            <Label htmlFor="labels">Labels (Optional)</Label>    const response = await restartInstanceRunnerInstanceIdRestartPost({

            <Input      path: {

              id="labels"        instance_id,

              name="labels"      },

              type="text"    });

              value={form.labels}

              onChange={handleChange}    if (response.data) {

              placeholder="e.g., linux,docker"      return { success: true, data: response.data as RunnerInstanceOut };

              className="mt-2"    }

              disabled={submitting || loading}

            />    return { success: false, message: "Failed to restart runner" };

            <p className="text-xs text-muted-foreground mt-1">  } catch (error: any) {

              Comma-separated labels for the runner    const detail = error?.message || "Failed to restart runner";

            </p>    return { success: false, message: detail };

          </div>  }

}

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={submitting || loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={submitting || loading}>
              {submitting || loading ? (
                <>
                  <Spinner />
                  {runner ? "Updating..." : "Creating..."}
                </>
              ) : runner ? (
                "Update Runner"
              ) : (
                "Create Runner"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
