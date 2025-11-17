import OpenAI from 'openai';
import { AppConfig, ImageProviderName } from './config';

export interface ImageRequest {
  prompt: string;
  width?: number;
  height?: number;
}

export interface ImageResult {
  url: string;
  altText: string;
  provider: ImageProviderName;
}

export interface ImageProvider {
  generatePoster(request: ImageRequest): Promise<ImageResult>;
}

export class ChatGptImageProvider implements ImageProvider {
  private client: OpenAI;
  private model: string;
  private width: number;
  private height: number;

  constructor(config: AppConfig) {
    if (!config.openaiApiKey) {
      throw new Error('OPENAI_API_KEY is required for the chatgpt image provider');
    }

    this.client = new OpenAI({ apiKey: config.openaiApiKey, baseURL: config.openaiBaseUrl });
    this.model = config.openaiModel;
    this.width = config.imageWidth;
    this.height = config.imageHeight;
  }

  async generatePoster(request: ImageRequest): Promise<ImageResult> {
    const response = await this.client.images.generate({
      model: this.model,
      prompt: request.prompt,
      size: `${request.width ?? this.width}x${request.height ?? this.height}`,
    });

    const imageUrl = response.data[0]?.url;
    if (!imageUrl) {
      throw new Error('Image generation succeeded but returned no URL');
    }

    return {
      url: imageUrl,
      altText: request.prompt,
      provider: 'chatgpt',
    };
  }
}

export class DummyImageProvider implements ImageProvider {
  async generatePoster(request: ImageRequest): Promise<ImageResult> {
    const width = request.width ?? 512;
    const height = request.height ?? 768;
    return {
      url: `https://placehold.co/${width}x${height}?text=Soviet+Poster`,
      altText: request.prompt,
      provider: 'dummy',
    };
  }
}

export const createImageProvider = (config: AppConfig): ImageProvider => {
  if (config.imageProvider === 'dummy') {
    return new DummyImageProvider();
  }

  return new ChatGptImageProvider(config);
};
