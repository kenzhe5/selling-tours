/** Parse SSE `data:` JSON lines into events; tolerate split TCP chunks. */
export function ingestSseChunks(
  buffer: string,
  chunk: string,
): { lines: Record<string, unknown>[]; remainder: string } {
  buffer += chunk;
  const parts = buffer.split('\n\n');
  const remainder = parts.pop() ?? '';
  const lines: Record<string, unknown>[] = [];
  for (const block of parts) {
    const line = block
      .split('\n')
      .find((row) => row.startsWith('data:'));
    if (!line) {
      continue;
    }
    const rawJson = line.replace(/^data:\s?/, '').trim();
    if (!rawJson) {
      continue;
    }
    try {
      lines.push(JSON.parse(rawJson) as Record<string, unknown>);
    } catch {
      /* ignore malformed line */
    }
  }
  return { lines, remainder };
}
