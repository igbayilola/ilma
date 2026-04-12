import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
        proxy: {
          '/api': {
            target: 'http://localhost:8000',
            changeOrigin: true,
          },
        },
      },
      plugins: [react()],
      build: {
        rollupOptions: {
          output: {
            manualChunks: {
              'vendor-react': ['react', 'react-dom', 'react-router-dom'],
              'vendor-ui': ['lucide-react', 'zustand'],
              'math': [
                './pages/student/ExercisePlayer.tsx',
                './components/exercise/QuestionRenderer.tsx',
              ],
              'exam': [
                './pages/student/ExamPlayer.tsx',
                './pages/student/ExamList.tsx',
                './pages/student/ExamCorrection.tsx',
              ],
              'admin': [
                './pages/admin/Dashboard.tsx',
                './pages/admin/Analytics.tsx',
                './pages/admin/Content.tsx',
                './pages/admin/Users.tsx',
              ],
              'teacher': [
                './pages/teacher/Dashboard.tsx',
                './pages/teacher/ClassroomDetail.tsx',
              ],
            },
          },
        },
      },
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
