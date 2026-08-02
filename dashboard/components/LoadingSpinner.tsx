#!/usr/bin/env ts-node
/**
 * LoadingSpinner.tsx --- inline loading indicator
 *
 * Contains:
 *   LoadingSpinner: renders a spinner with an accessible label
 */

/**
 * Renders a spinner with an accessible label.
 *
 * @returns spinner - Spinner element.
 */
export default function LoadingSpinner() {
  return (
    <div className="loading-spinner" role="status" aria-label="loading">
      loading…
    </div>
  );
}
