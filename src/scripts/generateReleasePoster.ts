import fs from 'fs';
import https from 'https';
import path from 'path';
import { execSync } from 'child_process';
import { loadConfig } from '../config';
import { createImageProvider } from '../imageProviders';
import { buildPosterPrompt, ChangedFileSummary, PullRequestSummary } from '../prompt';

const OUTPUT_PATH = process.env.POSTER_OUTPUT_PATH ?? path.resolve('assets/release-poster.png');

const parseRepoFromRemote = (remoteUrl: string): string | undefined => {
  const sshMatch = remoteUrl.match(/git@[^:]+:([^/]+\/[^.]+)(?:\.git)?/);
  if (sshMatch?.[1]) {
    return sshMatch[1];
  }

  const httpsMatch = remoteUrl.match(/https?:\/\/[^/]+\/([^/]+\/[^.]+)(?:\.git)?/);
  return httpsMatch?.[1];
};

const getRepoFullName = (): string => {
  const envRepo = process.env.GITHUB_REPOSITORY;
  if (envRepo) {
    return envRepo;
  }

  try {
    const remoteUrl = execSync('git config --get remote.origin.url', { encoding: 'utf8' }).trim();
    const parsed = parseRepoFromRemote(remoteUrl);
    if (parsed) {
      return parsed;
    }
  } catch (error) {
    console.warn('Unable to read git remote to determine repository name:', error);
  }

  return 'unknown/repo';
};

const getTagName = (): string => {
  return process.env.TAG_NAME || process.env.GITHUB_REF_NAME || 'untagged-release';
};

const getLatestCommitSummary = (): string => {
  try {
    return execSync('git log -1 --pretty=%s%n%n%b', { encoding: 'utf8' }).trim() || 'No description provided.';
  } catch (error) {
    console.warn('Unable to read latest commit message:', error);
    return 'No description provided.';
  }
};

const getChangedFiles = (): ChangedFileSummary[] => {
  try {
    const output = execSync('git diff --name-status HEAD^..HEAD', { encoding: 'utf8' });
    return output
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [status, filename] = line.split(/\s+/, 2);
        return { filename, status } as ChangedFileSummary;
      });
  } catch (error) {
    console.warn('Unable to read changed files for latest commit:', error);
    return [];
  }
};

const downloadImage = async (url: string, destination: string): Promise<void> =>
  new Promise((resolve, reject) => {
    https
      .get(url, (response) => {
        if (
          response.statusCode &&
          [301, 302, 303, 307, 308].includes(response.statusCode) &&
          response.headers.location
        ) {
          response.destroy();
          downloadImage(response.headers.location, destination).then(resolve).catch(reject);
          return;
        }

        if (response.statusCode && response.statusCode >= 400) {
          reject(new Error(`Failed to download image: status ${response.statusCode}`));
          return;
        }

        const dir = path.dirname(destination);
        fs.mkdirSync(dir, { recursive: true });
        const file = fs.createWriteStream(destination);
        response.pipe(file);
        file.on('finish', () => file.close(resolve));
        file.on('error', (error) => {
          fs.unlink(destination, () => reject(error));
        });
      })
      .on('error', (error) => {
        fs.unlink(destination, () => reject(error));
      });
  });

const main = async (): Promise<void> => {
  const repoFullName = getRepoFullName();
  const tagName = getTagName();
  const config = loadConfig();
  const provider = createImageProvider(config);

  const commitMessage = getLatestCommitSummary();
  const changedFiles = getChangedFiles();

  const releaseSummary: PullRequestSummary = {
    title: `Release ${tagName}`,
    body: commitMessage,
    number: 0,
    user: { login: process.env.GITHUB_ACTOR ?? 'automation' },
  };

  const prompt = buildPosterPrompt({
    basePrompt: config.posterPrompt,
    repoFullName,
    pr: releaseSummary,
    files: changedFiles,
    maxFiles: config.maxFiles,
  });

  console.log('Generating release poster using provider:', config.imageProvider);
  const image = await provider.generatePoster({
    prompt,
    width: config.imageWidth,
    height: config.imageHeight,
  });

  await downloadImage(image.url, OUTPUT_PATH);
  console.log(
    JSON.stringify(
      {
        outputPath: OUTPUT_PATH,
        provider: image.provider,
        prompt,
      },
      null,
      2,
    ),
  );
};

main().catch((error) => {
  console.error('Failed to generate release poster:', error);
  process.exitCode = 1;
});
