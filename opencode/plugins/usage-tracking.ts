/**
 * Flat entry file for the usage-tracking plugin (OpenCode auto-discovery).
 *
 * OpenCode only discovers plugins whose entry file sits directly in the
 * plugins directory, so this thin re-export forwards to the real
 * implementation in `usage-tracking/index.ts`. Keep it flat and dependency-
 * free; all logic lives in the subdirectory.
 */

export { default } from "./usage-tracking/index.ts";
