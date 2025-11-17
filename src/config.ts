import dotenv from 'dotenv';

dotenv.config();

export type ImageProviderName = 'chatgpt' | 'dummy';

export interface AppConfig {
  allowedRepos: Set<string>;
  imageProvider: ImageProviderName;
  openaiApiKey?: string;
  openaiModel: string;
  openaiBaseUrl?: string;
  posterPrompt: string;
  maxFiles: number;
  imageWidth: number;
  imageHeight: number;
}

const defaultPrompt =
  'Generate a high-contrast Soviet propaganda style poster that celebrates the collaboration in this pull request. Include bold geometric shapes, expressive characters, and heroic lighting.';

export const loadConfig = (): AppConfig => {
  const allowedReposEnv = process.env.ALLOWED_REPOS;
  const allowedRepos = allowedReposEnv
    ? new Set(
        allowedReposEnv
          .split(',')
          .map((entry) => entry.trim())
          .filter(Boolean),
      )
    : new Set<string>();

  const imageProvider = (process.env.IMAGE_PROVIDER as ImageProviderName | undefined) ?? 'chatgpt';

  const openaiApiKey = process.env.OPENAI_API_KEY;
  const openaiModel = process.env.OPENAI_IMAGE_MODEL ?? 'gpt-image-1';
  const openaiBaseUrl = process.env.OPENAI_BASE_URL;

  const posterPrompt = process.env.POSTER_PROMPT ?? defaultPrompt;

  const maxFiles = Number.parseInt(process.env.MAX_FILES ?? '10', 10);
  const imageWidthEnv = process.env.IMAGE_WIDTH ?? process.env.IMAGE_SIZE ?? '1024';
  const imageHeightEnv = process.env.IMAGE_HEIGHT ?? process.env.IMAGE_SIZE ?? '1536';
  const imageWidth = Number.parseInt(imageWidthEnv, 10);
  const imageHeight = Number.parseInt(imageHeightEnv, 10);

  return {
    allowedRepos,
    imageProvider,
    openaiApiKey,
    openaiModel,
    openaiBaseUrl,
    posterPrompt,
    maxFiles: Number.isNaN(maxFiles) ? 10 : maxFiles,
    imageWidth: Number.isNaN(imageWidth) ? 1024 : imageWidth,
    imageHeight: Number.isNaN(imageHeight) ? 1536 : imageHeight,
  };
};
