#!/usr/bin/env ts-node
/**
 * api.ts --- typed client for the llmjudge results API
 *
 * Contains:
 *   fetchRuns: lists recent runs from the API
 *   fetchRun: fetches one run with scores
 */

export interface RunSummary {
  id: string;
  repo: string;
  status: string;
  created_at: string;
}

export interface RunDetail extends RunSummary {
  scores: Record<string, number>;
}

const API_BASE = "/api";

/**
 * Lists recent runs from the API.
 *
 * @param repo - Optional repo filter.
 * @returns runs - Run summaries newest-first.
 */
export async function fetchRuns(repo?: string): Promise<RunSummary[]> {
  const query = repo ? `?repo=${encodeURIComponent(repo)}` : "";
  const response = await fetch(`${API_BASE}/runs${query}`);
  return response.json();
}

/**
 * Fetches one run with its scores.
 *
 * @param runId - Run identifier.
 * @returns run - Run payload with scores.
 */
export async function fetchRun(runId: string): Promise<RunDetail> {
  const response = await fetch(`${API_BASE}/runs/${runId}`);
  return response.json();
}

/**
 * Lists repos that have at least one stored run.
 *
 * @returns repos - Sorted distinct repo names.
 */
export async function fetchRepos(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/repos`);
  return response.json();
}
