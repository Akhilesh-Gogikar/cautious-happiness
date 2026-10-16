import { useSyncExternalStore } from "react";

const subscribe = () => () => {};

/** False while server-rendering and hydrating, true afterwards. */
export function useIsClient(): boolean {
  return useSyncExternalStore(subscribe, () => true, () => false);
}
