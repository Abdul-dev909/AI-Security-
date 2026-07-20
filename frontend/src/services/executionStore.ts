import type { ExecutionEntry, Attack, AttackResult } from '../types';

let executions: ExecutionEntry[] = [];

/**
 * Generates an execution ID using the attack ID and timestamp without spaces.
 */
function generateExecutionId(attackId: string): string {
  const now = new Date();
  const timestamp = now.toISOString().replace(/[-:T]/g, '').split('.')[0];
  return `${attackId}-${timestamp}`;
}

export function addExecution(attack: Attack, result: AttackResult): ExecutionEntry {
  const entry: ExecutionEntry = {
    id: generateExecutionId(attack.id),
    timestamp: new Date().toISOString(),
    attack,
    result,
  };

  executions.unshift(entry);

  if (executions.length > 50) {
    executions.pop();
  }

  return entry;
}

export function getExecution(id: string): ExecutionEntry | undefined {
  return executions.find((e) => e.id === id);
}

export function getAllExecutions(): ExecutionEntry[] {
  return [...executions];
}

export function clearExecutions(): void {
  executions = [];
}
