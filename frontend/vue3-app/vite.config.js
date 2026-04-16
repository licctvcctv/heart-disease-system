import path from 'node:path';
import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
export default defineConfig(function (_a) {
    var mode = _a.mode;
    var env = loadEnv(mode, process.cwd(), '');
    var backendUrl = env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
    var port = Number(env.VITE_PORT || 5173);
    return {
        plugins: [vue()],
        resolve: {
            alias: {
                '@': path.resolve(__dirname, 'src'),
            },
        },
        server: {
            host: '0.0.0.0',
            port: port,
            proxy: {
                '/api': {
                    target: backendUrl,
                    changeOrigin: true,
                },
            },
        },
        preview: {
            host: '0.0.0.0',
            port: Number(env.VITE_PREVIEW_PORT || 4173),
        },
    };
});
