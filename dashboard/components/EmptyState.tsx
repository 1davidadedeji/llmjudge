#!/usr/bin/env ts-node
/**
 * EmptyState.tsx --- placeholder shown when a view has no data
 *
 * Contains:
 *   EmptyState: renders a friendly empty message
 */

/**
 * Renders a friendly empty message.
 *
 * @param props.message - Message to display.
 * @returns block - Empty-state element.
 */
export default function EmptyState({ message }: { message: string }) {
  return <div className="empty-state">{message}</div>;
}
