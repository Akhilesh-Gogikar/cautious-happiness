export const DEFAULT_LLM_MODEL = "lfm-thinking";
export const DEFAULT_LLM_PROVIDER = "llama.cpp";
export const DEFAULT_LLAMA_CPP_URL = "http://localhost:8080";

export function getSelectedModel(): string {
  if (typeof window === "undefined") return DEFAULT_LLM_MODEL;
  return localStorage.getItem("POLY_MODEL") || DEFAULT_LLM_MODEL;
}

export function getLlamaCppUrl(): string {
  if (typeof window === "undefined") return DEFAULT_LLAMA_CPP_URL;
  return localStorage.getItem("LLAMA_CPP_URL") || DEFAULT_LLAMA_CPP_URL;
}
