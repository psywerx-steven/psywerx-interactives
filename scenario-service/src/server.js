import { createServer } from "node:http";
import OpenAI from "openai";
import { loadCatalog } from "./catalog.js";
import { loadConfig } from "./config.js";
import { createHttpHandler } from "./http-app.js";
import { createOperationalizer } from "./openai-service.js";

async function main() {
  const config = loadConfig();
  const catalog = loadCatalog();
  const openai = new OpenAI({
    apiKey: config.openAiApiKey,
    maxRetries: 0,
    timeout: config.openAiTimeoutMs,
  });
  const operationalize = createOperationalizer({
    client: openai,
    model: config.openAiModel,
    timeoutMs: config.openAiTimeoutMs,
    maxOutputTokens: config.openAiMaxOutputTokens,
  });
  const handler = createHttpHandler({ config, catalog, operationalize });
  const server = createServer(handler);
  server.requestTimeout = config.serverRequestTimeoutMs;
  server.headersTimeout = Math.min(10000, config.serverRequestTimeoutMs - 1000);
  server.keepAliveTimeout = 5000;
  server.maxRequestsPerSocket = 100;

  const shutdown = () => {
    server.close(() => process.exit(0));
    setTimeout(() => process.exit(1), 5000).unref();
  };
  process.once("SIGINT", shutdown);
  process.once("SIGTERM", shutdown);

  server.listen(config.port, config.host, () => {
    console.info(
      JSON.stringify({
        event: "service_started",
        host: config.host,
        port: config.port,
      })
    );
  });
}

main().catch(() => {
  console.error(JSON.stringify({ event: "service_start_failed" }));
  process.exitCode = 1;
});
