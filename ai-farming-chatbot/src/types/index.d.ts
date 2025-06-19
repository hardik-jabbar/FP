interface UserQuery {
    query: string;
    userId: string;
}

interface ChatGPTResponse {
    response: string;
    usage: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
    };
}

interface FarmingKnowledge {
    crops: string[];
    tractors: string[];
    parts: string[];
    gps: string[];
    landMapping: string[];
    cropYieldImprovement: string[];
}

interface ApiResponse {
    success: boolean;
    data?: ChatGPTResponse | FarmingKnowledge;
    error?: string;
}