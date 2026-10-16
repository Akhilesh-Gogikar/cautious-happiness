import { useSyncExternalStore } from "react";

export const DEFAULT_LLM_MODEL = "lfm-thinking";
export const DEFAULT_LLM_PROVIDER = "llama.cpp";
export const DEFAULT_LLAMA_CPP_URL = "http://localhost:8080";

/** Fired on window when this tab saves the config; other tabs get a 'storage' event. */
const CONFIG_CHANGE_EVENT = "llm-config-change";

export function getSelectedModel(): string {
  if (typeof window === "undefined") return DEFAULT_LLM_MODEL;
  return localStorage.getItem("POLY_MODEL") || DEFAULT_LLM_MODEL;
}

export function getLlamaCppUrl(): string {
  if (typeof window === "undefined") return DEFAULT_LLAMA_CPP_URL;
  return localStorage.getItem("LLAMA_CPP_URL") || DEFAULT_LLAMA_CPP_URL;
}

export function saveLlmConfig(model: string, llamaCppUrl: string) {
  localStorage.setItem("POLY_MODEL", model || DEFAULT_LLM_MODEL);
  localStorage.setItem("LLAMA_CPP_URL", llamaCppUrl || DEFAULT_LLAMA_CPP_URL);
  window.dispatchEvent(new Event(CONFIG_CHANGE_EVENT));
}

function subscribeToConfig(onChange: () => void) {
  window.addEventListener("storage", onChange);
  window.addEventListener(CONFIG_CHANGE_EVENT, onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(CONFIG_CHANGE_EVENT, onChange);
  };
}

/** The selected model; follows saves in this tab and in other tabs. The default while server-rendering. */
export function useSelectedModel(): string {
  return useSyncExternalStore(subscribeToConfig, getSelectedModel, () => DEFAULT_LLM_MODEL);
}
