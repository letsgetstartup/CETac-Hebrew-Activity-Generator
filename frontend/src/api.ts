import type { ActivityResponse, GenerateRequest } from "./types";

// In production, this would be your Cloud Function URL
// specific logic: emulate locally means pointing to specific port
// Since we haven't deployed, we will assume local emulation port 5001 or using Vite proxy
// In production, we use the rewrite rule /api/generate -> function
const API_URL = "/api/generate";

export const generateActivity = async (request: GenerateRequest): Promise<ActivityResponse> => {
    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(request),
        });

        const data = await response.json();

        // In emulator, sometimes you get different error formats, handle gently
        if (!response.ok) {
            return {
                success: false,
                error: data.error || "HTTP_ERROR",
                message: data.message || `Status ${response.status}: ${response.statusText}`
            };
        }

        return data as ActivityResponse;
    } catch (error) {
        console.error("API Call Failed:", error);
        return {
            success: false,
            error: "NETWORK_ERROR",
            message: error instanceof Error ? error.message : "Unknown network error"
        };
    }
};
