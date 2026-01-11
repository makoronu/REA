/**
 * Markdownパーサー
 * MDファイルを構造化データに変換する
 */

import { ParsedHelp, HelpSection, HelpItem } from '../types/help';
import { HELP_BASE_PATH } from '../constants/help';

/**
 * 文字列をURL安全なIDに変換
 */
const toSlug = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

/**
 * MDテキストをパースして構造化データに変換
 */
export const parseMarkdown = (markdown: string): ParsedHelp => {
  const lines = markdown.split('\n');

  let title = '';
  let description = '';
  const sections: HelpSection[] = [];

  let currentSection: HelpSection | null = null;
  let currentItem: HelpItem | null = null;
  let contentBuffer: string[] = [];
  let foundTitle = false;
  let foundDescription = false;

  const flushContent = () => {
    if (currentItem && contentBuffer.length > 0) {
      currentItem.content = contentBuffer.join('\n').trim();
      contentBuffer = [];
    }
  };

  const flushItem = () => {
    flushContent();
    if (currentItem && currentSection) {
      currentSection.items.push(currentItem);
      currentItem = null;
    }
  };

  const flushSection = () => {
    flushItem();
    if (currentSection) {
      sections.push(currentSection);
      currentSection = null;
    }
  };

  for (const line of lines) {
    // # タイトル
    if (line.startsWith('# ') && !foundTitle) {
      title = line.slice(2).trim();
      foundTitle = true;
      continue;
    }

    // タイトル直後の説明文（最初の非空行）
    if (foundTitle && !foundDescription && line.trim() && !line.startsWith('#') && !line.startsWith('---')) {
      description = line.trim();
      foundDescription = true;
      continue;
    }

    // ## セクション
    if (line.startsWith('## ')) {
      flushSection();
      const sectionTitle = line.slice(3).trim();
      currentSection = {
        id: toSlug(sectionTitle),
        title: sectionTitle,
        items: [],
      };
      continue;
    }

    // ### 項目
    if (line.startsWith('### ')) {
      flushItem();
      const itemTitle = line.slice(4).trim();
      currentItem = {
        id: toSlug(itemTitle),
        title: itemTitle,
        content: '',
      };
      continue;
    }

    // コンテンツ行（セクション区切り---はスキップ）
    if (currentItem && line.trim() !== '---') {
      contentBuffer.push(line);
    }
  }

  // 最後のセクション/項目をフラッシュ
  flushSection();

  return { title, description, sections };
};

/**
 * MDファイルを取得してパース
 */
export const fetchAndParseMarkdown = async (filename: string): Promise<ParsedHelp> => {
  const url = `${HELP_BASE_PATH}/${filename}`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status}`);
  }

  const markdown = await response.text();
  return parseMarkdown(markdown);
};

/**
 * 用語集用: 見出しのみ抽出（検索用）
 */
export const extractHeadings = (markdown: string): string[] => {
  const lines = markdown.split('\n');
  const headings: string[] = [];

  for (const line of lines) {
    if (line.startsWith('### ')) {
      headings.push(line.slice(4).trim());
    }
  }

  return headings;
};
