import { Probot, Context } from 'probot';
import { loadConfig } from './config';
import { createImageProvider } from './imageProviders';
import { buildPosterPrompt, ChangedFileSummary, PullRequestSummary } from './prompt';

type PullRequestPayload = Context<'pull_request'>['payload'];

type PullRequestEventName =
  | 'pull_request.opened'
  | 'pull_request.reopened'
  | 'pull_request.synchronize'
  | 'pull_request.ready_for_review';

const config = loadConfig();
const imageProvider = createImageProvider(config);

const shouldProcessRepo = (repoFullName: string): boolean => {
  if (config.allowedRepos.size === 0) {
    return true;
  }

  return config.allowedRepos.has(repoFullName);
};

const buildPromptFromPayload = (
  payload: PullRequestPayload,
  files: ChangedFileSummary[],
): string => {
  const pr: PullRequestSummary = {
    title: payload.pull_request.title,
    body: payload.pull_request.body,
    number: payload.pull_request.number,
    html_url: payload.pull_request.html_url,
    user: payload.pull_request.user,
  };

  const repoFullName = payload.repository.full_name;

  return buildPosterPrompt({
    basePrompt: config.posterPrompt,
    repoFullName,
    pr,
    files,
    maxFiles: config.maxFiles,
  });
};

const fetchChangedFiles = async (context: Context<'pull_request'>): Promise<ChangedFileSummary[]> => {
  const { owner, name } = context.payload.repository;
  const pullNumber = context.payload.pull_request.number;
  const files: ChangedFileSummary[] = [];

  let page = 1;
  const perPage = 100;
  while (files.length < config.maxFiles) {
    const response = await context.octokit.pulls.listFiles({
      owner: owner.login,
      repo: name,
      pull_number: pullNumber,
      per_page: perPage,
      page,
    });

    files.push(
      ...response.data.map((file) => ({
        filename: file.filename,
        status: file.status,
        additions: file.additions,
        deletions: file.deletions,
      })),
    );

    if (response.data.length < perPage) {
      break;
    }

    page += 1;
  }

  return files;
};

const createCommentBody = (imageUrl: string, prompt: string, provider: string): string => {
  return [
    '🛠️ Generated Soviet-inspired propaganda poster for this PR!',
    '',
    `![Generated poster](${imageUrl})`,
    '',
    `<details>`,
    `<summary>Prompt (${provider})</summary>`,
    '',
    prompt,
    '</details>',
  ].join('\n');
};

const handlePullRequestEvent = async (context: Context<'pull_request'>): Promise<void> => {
  const repoFullName = context.payload.repository.full_name;
  if (!shouldProcessRepo(repoFullName)) {
    context.log.info(`Skipping PR for ${repoFullName} because it is not in the allowed list.`);
    return;
  }

  const changedFiles = await fetchChangedFiles(context);
  const prompt = buildPromptFromPayload(context.payload, changedFiles);

  try {
    const image = await imageProvider.generatePoster({
      prompt,
      width: config.imageWidth,
      height: config.imageHeight,
    });
    const comment = createCommentBody(image.url, prompt, image.provider);

    await context.octokit.issues.createComment({
      owner: context.payload.repository.owner.login,
      repo: context.payload.repository.name,
      issue_number: context.payload.pull_request.number,
      body: comment,
    });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    context.log.error({ error }, 'Failed to generate image');
    await context.octokit.issues.createComment({
      owner: context.payload.repository.owner.login,
      repo: context.payload.repository.name,
      issue_number: context.payload.pull_request.number,
      body: `❗ Unable to generate poster: ${errorMessage}`,
    });
  }
};

export default (app: Probot): void => {
  const events: PullRequestEventName[] = [
    'pull_request.opened',
    'pull_request.reopened',
    'pull_request.synchronize',
    'pull_request.ready_for_review',
  ];
  app.on(events, handlePullRequestEvent);
};
