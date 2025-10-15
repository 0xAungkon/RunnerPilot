import apiClient from "@/lib/api/client";

interface RegisterApiParams {
	email: string;
	password: string;
	firstname: string;
	lastname: string;
}

export async function registerApi({ email, password, firstname, lastname }: RegisterApiParams) {
	try {
		const response = await apiClient.post("auth/register", {
			email,
			password,
			first_name: firstname,
			last_name: lastname,
		});
		return { success: true, data: response.data };
	} catch (error) {
		if ((error as any).response) {
			// Django error format
			const errData = (error as any).response.data;
			let message = "Registration failed.";
			if (errData.password) message = errData.password[0];
			else if (errData.email) message = errData.email[0];
			else if (errData.detail) message = errData.detail;
			return { success: false, message };
		}
		return { success: false, message: "Network error. Please try again." };
	}
}
