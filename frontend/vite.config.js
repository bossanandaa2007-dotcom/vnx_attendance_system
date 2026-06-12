import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

function dashboardLinks() {
  return {
    name: "dashboard-links",
    configureServer(server) {
      server.httpServer?.once("listening", () => {
        const address = server.httpServer.address();
        const port = typeof address === "object" && address ? address.port : 5173;
        const local = `http://localhost:${port}`;
        const network = server.resolvedUrls?.network?.[0]?.replace(/\/$/, "");

        console.log("");
        console.log("  Dashboards:");
        console.log(`  Admin local:    ${local}/`);
        console.log(`  Mobile local:   ${local}/mobile`);

        if (network) {
          console.log(`  Admin network:  ${network}/`);
          console.log(`  Mobile network: ${network}/mobile`);
        }

        console.log("");
      });
    }
  };
}

export default defineConfig({
  plugins: [react(), dashboardLinks()],
  server: {
    host: "0.0.0.0",
    port: 5173
  }
});
