export function createRateLimiter({ windowMs, maxRequests, maxKeys, now = Date.now }) {
  const entries = new Map();

  function removeExpired(currentTime) {
    for (const [key, value] of entries) {
      if (currentTime - value.windowStartedAt >= windowMs) entries.delete(key);
    }
  }

  function boundSize(currentTime) {
    if (entries.size < maxKeys) return;
    removeExpired(currentTime);
    while (entries.size >= maxKeys) {
      const oldest = entries.keys().next().value;
      if (oldest === undefined) break;
      entries.delete(oldest);
    }
  }

  function consume(key) {
    const currentTime = now();
    let entry = entries.get(key);
    if (!entry || currentTime - entry.windowStartedAt >= windowMs) {
      boundSize(currentTime);
      entry = { count: 0, windowStartedAt: currentTime };
      entries.set(key, entry);
    }
    const resetMs = Math.max(1, windowMs - (currentTime - entry.windowStartedAt));
    if (entry.count >= maxRequests) {
      return { allowed: false, remaining: 0, resetMs };
    }
    entry.count += 1;
    return {
      allowed: true,
      remaining: Math.max(0, maxRequests - entry.count),
      resetMs,
    };
  }

  return Object.freeze({ consume });
}
