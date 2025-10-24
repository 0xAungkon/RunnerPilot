import { } from "@/lib/api/";

import { loginAuthLoginPost } from "@/lib/api";
import type { TokenResponse } from "@/lib/api";

export async function loginApi({ username, password }: { username: string; password: string }) {
	try {
		const response = await loginAuthLoginPost({
			body: {
				email: username,
				password,
			},
		});
		
		if (response.data) {
			return { success: true, data: response.data as TokenResponse };
		}
		
		return { success: false, message: "Login failed" };
	} catch (error: any) {
		// Handle Hey API error format
		const detail = error?.message || "Login failed";
		return { success: false, message: detail };
	}
}