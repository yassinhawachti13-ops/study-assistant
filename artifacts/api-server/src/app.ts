import express, { type Express } from "express";
import cors from "cors";
import pinoHttp from "pino-http";
import router from "./routes";
import { logger } from "./lib/logger";

const app: Express = express();

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
    },
  }),
);
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

// The Python Flask app is the user-facing web app in this project.
// Forward non-API preview requests to it because the application router
// currently sends the root preview through this registered service.
app.use(async (req, res, next) => {
  if (req.path === "/api" || req.path.startsWith("/api/")) {
    return next();
  }

  try {
    const requestHeaders = new Headers();
    const contentType = req.get("content-type");
    const accept = req.get("accept");
    const cookie = req.get("cookie");

    if (contentType) requestHeaders.set("content-type", contentType);
    if (accept) requestHeaders.set("accept", accept);
    if (cookie) requestHeaders.set("cookie", cookie);

    const fetchOptions: RequestInit = {
      method: req.method,
      headers: requestHeaders,
      redirect: "manual",
    };

    if (req.method !== "GET" && req.method !== "HEAD") {
      if (contentType?.includes("application/x-www-form-urlencoded")) {
        fetchOptions.body = new URLSearchParams(req.body as Record<string, string>);
      } else if (contentType?.includes("application/json")) {
        fetchOptions.body = JSON.stringify(req.body);
      }
    }

    const flaskResponse = await fetch(
      `http://127.0.0.1:5000${req.originalUrl}`,
      fetchOptions,
    );

    res.status(flaskResponse.status);
    flaskResponse.headers.forEach((value, key) => {
      // Express calculates these headers for the forwarded response.
      if (!["content-encoding", "content-length", "transfer-encoding"].includes(key)) {
        res.setHeader(key, value);
      }
    });
    res.send(Buffer.from(await flaskResponse.arrayBuffer()));
  } catch (error) {
    req.log.error({ err: error }, "Could not forward preview request to Flask");
    next(error);
  }
});

export default app;
