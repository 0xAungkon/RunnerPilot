import apiClient from "@/lib/api/client";
import { toast } from "sonner"

export async function loginApi({ username, password }) {
	try {
		const response = await apiClient.post("auth/login", {
			username,
			password,
		});
		return { success: true, data: response.data };
	} catch (error) {
		if (error.response) {
			// Django error format
			const detail = error.response.data?.detail?.[0] || "Login failed";
			return { success: false, message: detail };
		}
		return { success: false, message: "Network error. Please try again." };
	}
}