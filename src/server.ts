import http from "node:http";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

type ElisChatResponse = {
  message?: { role?: string; content?: string };
  response?: string;
  model?: string;
};

const PORT = Number.parseInt(process.env.PORT ?? "3333", 10);
const ELIS_BASE_URL = (process.env.ELIS_BASE_URL ?? "http://localhost:11434").replace(
  /\/$/,
  ""
);
const ELIS_MODEL = process.env.ELIS_MODEL ?? "elis:latest";

const mcp = new McpServer({ name: "elis-mcp", version: "0.1.0" });

mcp.registerTool(
  "ask_elis",
  {
    title: "Perguntar para a ELIS",
    description: "Envia um prompt para a ELIS (Ollama) e retorna o texto da resposta.",
    inputSchema: { prompt: z.string() },
    outputSchema: { text: z.string() },
  },
  async ({ prompt }) => {
    const url = `${ELIS_BASE_URL}/api/chat`;
    const payload = {
      model: ELIS_MODEL,
      stream: false,
      messages: [{ role: "user", content: prompt }],
    };

    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const errText = await resp.text().catch(() => "");
      const text = `Erro ELIS HTTP ${resp.status}: ${errText || resp.statusText}`;
      return { content: [{ type: "text", text }], structuredContent: { text } };
    }

    const data = (await resp.json()) as ElisChatResponse;
    const text = data?.message?.content ?? data?.response ?? JSON.stringify(data);

    return { content: [{ type: "text", text }], structuredContent: { text } };
  }
);

function readJsonBody(req: http.IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => {
      if (!raw) return resolve({});
      try {
        resolve(JSON.parse(raw));
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "GET" && req.url === "/health") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    if (req.method === "POST" && req.url === "/mcp") {
      const body = await readJsonBody(req);
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
        enableJsonResponse: true,
      });

      res.on("close", () => {
        transport.close();
      });

      await mcp.connect(transport);
      // SDK espera algo compatível com req/res do Node. O `body` já é o JSON parseado.
      await transport.handleRequest(req, res, body as never);
      return;
    }

    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not found");
  } catch (err) {
    res.writeHead(500, { "Content-Type": "text/plain" });
    res.end(`Server error: ${String(err)}`);
  }
});

server.listen(PORT, () => {
  console.log(`MCP server: http://localhost:${PORT}/mcp`);
  console.log(`Health: http://localhost:${PORT}/health`);
  console.log(`ELIS_BASE_URL=${ELIS_BASE_URL}`);
  console.log(`ELIS_MODEL=${ELIS_MODEL}`);
});
