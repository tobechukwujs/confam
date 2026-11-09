import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Monorepo root, so workspace packages are traced and the lockfile warning goes away.
  outputFileTracingRoot: path.join(here, "../.."),
  transpilePackages: ["@confam/i18n", "@confam/contract"],
  poweredByHeader: false,
  reactStrictMode: true,
};

export default nextConfig;
