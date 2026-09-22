import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow connections from the local network IP to fix React/HMR CORS blocks
  allowedDevOrigins: ['10.185.91.109', 'localhost']
};

export default nextConfig;
