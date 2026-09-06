import { fileURLToPath, URL } from "node:url";

export default {
  resolve: {
    alias: {
      react: fileURLToPath(new URL("../../../../../../frontend/node_modules/react", import.meta.url)),
      "react-dom/client": fileURLToPath(new URL("../../../../../../frontend/node_modules/react-dom/client.js", import.meta.url)),
    },
  },
};
