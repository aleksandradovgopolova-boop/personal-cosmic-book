/* eslint-disable */
import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import { useReadingSync } from './use-reading-sync.js';
import './reader.css';

// ───────── DATA ─────────
const PAGES = [
  { n: 1,  src: 'pages/page-001-cover.webp',           kind: 'cover',      chapter: 0 },
  { n: 2,  src: 'pages/page-002-disclaimer.webp',      kind: 'disclaimer', chapter: 0 },
  {
    n: 3,
    src: 'pages/page-003-song.webp',
    kind: 'song',
    chapter: 0,
    href: 'https://youtu.be/M5MkEv9VY3c?si=tj_eYJxpTVBlZQa-',
  },
  { n: 4,  src: 'pages/page-004-dedication.webp',      kind: 'dedication', chapter: 0 },
  { n: 5,  src: 'pages/page-005-chapter-01-title.webp', kind: 'title',      chapter: 1 },
  {
    n: 6,
    src: 'pages/page-006-chapter-01-song.webp',
    kind: 'song',
    chapter: 1,
    href: 'https://youtu.be/z2DwOUKgWzs?si=rGhaOfmPeCuAYaqy',
  },
  { n: 7,  src: 'pages/page-007-chapter-01-text.webp',  kind: 'text',  chapter: 1 },
  { n: 8,  src: 'pages/page-008-chapter-01-text.webp',  kind: 'text',  chapter: 1 },
  { n: 9,  src: 'pages/page-009-chapter-01-text.webp',  kind: 'text',  chapter: 1 },
  { n: 10, src: 'pages/page-010-chapter-01-text.webp',  kind: 'text',  chapter: 1 },
  { n: 11, src: 'pages/page-011-chapter-01-image.webp', kind: 'image', chapter: 1 },
  { n: 12, src: 'pages/page-012-chapter-02-title.webp', kind: 'title', chapter: 2 },
  {
    n: 13,
    src: 'pages/page-013-chapter-02-song.webp',
    kind: 'song',
    chapter: 2,
    href: 'https://youtu.be/HEQNdQrApR0?si=u8jM8NZ_fl0T-T2d',
  },
  { n: 14, src: 'pages/page-014-chapter-02-text.webp',  kind: 'text',  chapter: 2 },
  { n: 15, src: 'pages/page-015-chapter-02-text.webp',  kind: 'text',  chapter: 2 },
  { n: 16, src: 'pages/page-016-chapter-02-text.webp',  kind: 'text',  chapter: 2 },
  { n: 17, src: 'pages/page-017-chapter-02-text.webp',  kind: 'text',  chapter: 2 },
  { n: 18, src: 'pages/page-018-chapter-02-text.webp',  kind: 'text',  chapter: 2 },
  { n: 19, src: 'pages/page-019-chapter-02-text.webp',  kind: 'text',  chapter: 2 },
  { n: 20, src: 'pages/page-020-chapter-02-image.webp', kind: 'image', chapter: 2 },
  { n: 21, src: 'pages/page-021-chapter-02-image.webp', kind: 'image', chapter: 2 },
  { n: 22, src: 'pages/page-022-chapter-03-title.webp', kind: 'title', chapter: 3 },
  {
    n: 23,
    src: 'pages/page-023-chapter-03-song.webp',
    kind: 'song',
    chapter: 3,
    href: 'https://youtu.be/-LAcaESjaHE?si=Sl2xe-MuM32B32-B',
  },
  { n: 24, src: 'pages/page-024-chapter-03-text.webp',  kind: 'text',  chapter: 3 },
  { n: 25, src: 'pages/page-025-chapter-03-text.webp',  kind: 'text',  chapter: 3 },
  { n: 26, src: 'pages/page-026-chapter-03-image.webp', kind: 'image', chapter: 3 },
  { n: 27, src: 'pages/page-027-chapter-03-text.webp',  kind: 'text',  chapter: 3 },
  { n: 28, src: 'pages/page-028-chapter-03-text.webp',  kind: 'text',  chapter: 3 },
  { n: 29, src: 'pages/page-029-chapter-03-image.webp', kind: 'image', chapter: 3 },
  { n: 30, src: 'pages/page-030-chapter-03-text.webp',  kind: 'text',  chapter: 3 },
  { n: 31, src: 'pages/page-031-chapter-03-text.webp',  kind: 'text',  chapter: 3 },
  { n: 32, src: 'pages/page-032-chapter-03-text.webp',  kind: 'text',  chapter: 3 },
  { n: 33, src: 'pages/page-033-chapter-03-text.webp',  kind: 'image', chapter: 3 },
  { n: 34, src: 'pages/page-034-chapter-04-title.webp', kind: 'title', chapter: 4 },
  {
    n: 35,
    src: 'pages/page-035-chapter-04-song.webp',
    kind: 'song',
    chapter: 4,
    href: 'https://youtu.be/jnyWJbSJVAE?si=ln6UF91EJ5Q-WNo8',
  },
  { n: 36, src: 'pages/page-036-chapter-04-text.webp',  kind: 'text',  chapter: 4 },
  { n: 37, src: 'pages/page-037-chapter-04-image.webp', kind: 'image', chapter: 4 },
  { n: 38, src: 'pages/page-038-chapter-04-text.webp',  kind: 'text',  chapter: 4 },
  { n: 39, src: 'pages/page-039-chapter-04-image.webp', kind: 'image', chapter: 4 },
  { n: 40, src: 'pages/page-040-chapter-04-text.webp',  kind: 'text',  chapter: 4 },
  { n: 41, src: 'pages/page-041-chapter-04-text.webp',  kind: 'text',  chapter: 4 },
  { n: 42, src: 'pages/page-042-chapter-05-title.webp', kind: 'title', chapter: 5 },
  {
    n: 43,
    src: 'pages/page-043-chapter-05-song.webp',
    kind: 'song',
    chapter: 5,
    href: 'https://www.youtube.com/watch?v=m9DO3zpdWqw',
  },
  { n: 44, src: 'pages/page-044-chapter-05-text.webp',  kind: 'text',  chapter: 5 },
  { n: 45, src: 'pages/page-045-chapter-05-text.webp',  kind: 'text',  chapter: 5 },
  { n: 46, src: 'pages/page-046-chapter-05-text.webp',  kind: 'text',  chapter: 5 },
  { n: 47, src: 'pages/page-047-chapter-05-text.webp',  kind: 'text',  chapter: 5 },
  { n: 48, src: 'pages/page-048-chapter-05-text.webp',  kind: 'text',  chapter: 5 },
  { n: 49, src: 'pages/page-049-chapter-05-text.webp',  kind: 'text',  chapter: 5 },
];

const CHAPTERS = [
  { num: '01', title: 'У самурая свой путь',       firstPage: 5,  page: 5,  pages: 7,  free: true  },
  { num: '02', title: 'Вывернуть наизнанку',       firstPage: 12, page: 12, pages: 10, free: false },
  { num: '03', title: 'Счастливый билетик',        firstPage: 22, page: 22, pages: 12, free: false },
  { num: '04', title: 'Чёртов борщ',               firstPage: 34, page: 34, pages: 8,  free: false },
  { num: '05', title: 'На восьмом этаже',          firstPage: 42, page: 42, pages: 8,  free: false },
  { num: '06', title: 'Шляпная коробка',           firstPage: null, page: null, pages: 0, free: false },
  { num: '07', title: 'Тёмные паттерны',           firstPage: null, page: null, pages: 0, free: false },
  { num: '08', title: 'Прости меня, моя любовь',   firstPage: null, page: null, pages: 0, free: false },
  { num: '09', title: 'Синяя борода',              firstPage: null, page: null, pages: 0, free: false },
  { num: '10', title: 'Москва слезам не верит',    firstPage: null, page: null, pages: 0, free: false },
];

const PRICE = '499 ₽';
const NAV_PRICE = '499 Р';
const PREVIEW_ALL_CHAPTERS = true;
const LAST_FREE_PAGE = 11;       // last page of chapter 1
const FIRST_PAID_PAGE = 12;      // first page after paywall
const TOTAL_PAGES = PAGES.length;
const STORAGE_KEY = 'bnbm_state_v2';
const INTRO_STORAGE_KEY = 'bnbm_intro_seen_v3';
const INTRO_VIDEO_SRC = 'media/intro-video.mp4';

function readLocalState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
    const hasSavedProgress = typeof saved?.lastPage === 'number';

    return {
      paid: typeof saved?.paid === 'boolean' ? saved.paid : false,
      lastPage: hasSavedProgress ? saved.lastPage : 2,
      updatedAt: typeof saved?.updatedAt === 'number'
        ? saved.updatedAt
        : hasSavedProgress
        ? Date.now()
        : 0,
    };
  } catch (error) {
    return { paid: false, lastPage: 2, updatedAt: 0 };
  }
}

// ───────── PAGE COMPONENT ─────────
function BookPage({ page, dim }) {
  if (!page) {
    return (
      <div className="bp bp--empty" aria-hidden="true">
        <div className="bp__inner" />
      </div>
    );
  }
  const image = (
    <img src={page.src} alt={`Страница ${page.n}`} draggable="false" loading="lazy" />
  );

  return (
    <div className={`bp ${page.href ? 'bp--linked' : ''} ${dim ? 'bp--dim' : ''}`}>
      <div className="bp__inner">
        {page.href ? (
          <a
            className="bp__page-link"
            href={page.href}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Открыть песню в YouTube"
          >
            {image}
          </a>
        ) : image}
      </div>
    </div>
  );
}

function BookMockup({ src, alt }) {
  return (
    <div className="book-mockup">
      <div className="book-mockup__book">
        <img
          className="book-mockup__cover"
          src={src}
          alt={alt}
          draggable="false"
        />
        <div className="book-mockup__spine" aria-hidden="true" />
      </div>
    </div>
  );
}

// ───────── INTRO PREVIEW ─────────
function IntroPreview({ onDone }) {
  const finishIntro = useCallback(() => {
    try { localStorage.setItem(INTRO_STORAGE_KEY, 'true'); } catch (e) {}
    onDone();
  }, [onDone]);

  return (
    <section className="intro" data-screen-label="00 Intro">
      <div className="intro__media-shell">
        <video
          className="intro__video"
          src={INTRO_VIDEO_SRC}
          autoPlay
          muted
          defaultMuted
          preload="auto"
          playsInline
          onEnded={finishIntro}
          onError={finishIntro}
          onCanPlay={(event) => {
            const video = event.currentTarget;
            video.muted = true;
            video.play().catch(() => {});
          }}
        />
      </div>
    </section>
  );
}

// ───────── WELCOME SCREEN ─────────
function SyncControl({ sync, onClick }) {
  const label = !sync.configured
    ? 'Локально'
    : !sync.user
    ? 'Прогресс'
    : sync.syncStatus === 'saving'
    ? 'Сохраняем…'
    : sync.syncStatus === 'error'
    ? 'Нет связи'
    : 'Сохранено';

  return (
    <button
      className={`sync-control sync-control--${sync.syncStatus}`}
      onClick={onClick}
      title={sync.user?.email || label}
      aria-label={sync.user?.email ? `${label}: ${sync.user.email}` : label}
    >
      <span className="sync-control__dot" aria-hidden="true" />
      <span>{label}</span>
    </button>
  );
}

function Welcome({ onOpen, onToc, onBuy, paid, sync, onSync }) {
  return (
    <section className="welcome" data-screen-label="01 Welcome">
      <header className="topbar topbar--welcome">
        <img
          className="welcome-garland"
          src="/icons/book-web-icons/doodle-party-garland.svg"
          alt=""
          aria-hidden="true"
        />

        <div className="welcome-nav__center" aria-hidden="true" />

        <nav className="welcome-nav welcome-nav--right" aria-label="Навигация">
          <button className="welcome-nav__link" onClick={onToc}>Оглавление</button>
          <button className="welcome-nav__link site-buy-button" onClick={onBuy}>
            Купить — {NAV_PRICE}
          </button>
        </nav>
      </header>

      <div className="welcome-doodles" aria-hidden="true">
        <img
          className="welcome-doodle welcome-doodle--star welcome-doodle--star-red"
          src="/icons/book-web-icons/doodle-star-red.svg"
          alt=""
        />
        <img
          className="welcome-doodle welcome-doodle--star welcome-doodle--star-black"
          src="/icons/book-web-icons/doodle-star-blue.svg"
          alt=""
        />
        <img
          className="welcome-doodle welcome-doodle--star welcome-doodle--star-blue"
          src="/icons/book-web-icons/doodle-star-outline-yellow.svg"
          alt=""
        />
        <img
          className="welcome-doodle welcome-doodle--star welcome-doodle--star-yellow"
          src="/icons/book-web-icons/doodle-star-blue.svg"
          alt=""
        />
        <img
          className="welcome-doodle welcome-doodle--star welcome-doodle--star-red-small"
          src="/icons/book-web-icons/doodle-star-outline-yellow.svg"
          alt=""
        />
        <img
          className="welcome-doodle welcome-doodle--star welcome-doodle--star-blue-small"
          src="/icons/book-web-icons/doodle-star-red.svg"
          alt=""
        />
        <img
          className="welcome-doodle welcome-doodle--star welcome-doodle--star-black-small"
          src="/icons/book-web-icons/doodle-star-black.svg"
          alt=""
        />
        <img
          className="welcome-doodle welcome-doodle--kite"
          src="/icons/book-web-icons/doodle-kite.svg"
          alt=""
        />
      </div>

      <main className="hero">
        <div className="hero__cover-col">
          <div className="hero__cover-wrap" onClick={onOpen} role="button" tabIndex="0"
               aria-label="Открыть книгу"
               onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpen(); } }}>
            <BookMockup
              src="/pages/page-001-cover.webp"
              alt="Больше не буду меньше"
            />
          </div>
        </div>

        <div className="hero__text">
          <div className="hero__quote">
            <p>
              <span>Привет!</span>
              <br />
              {' '}Это мой дебютный роман.
            </p>
            <p>
              Честный автофикшн
              <br />
              {' '}о&nbsp;взрослении, семье и&nbsp;любви.
            </p>
          </div>

          <div className="hero__body">
            <p>
              История девочки, которая
              <br />
              {' '}устала быть хорошей.
            </p>
          </div>
        </div>

      </main>

      <img
        className="welcome__line"
        src="/icons/book-web-icons/line-main.svg"
        alt=""
        aria-hidden="true"
      />

      <a
        className="welcome__telegram"
        href="https://t.me/dovgopolovaa"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Написать автору в Telegram"
      >
        <img
          className="welcome__telegram-icon"
          src="/icons/book-web-icons/doodle-paper-plane-trail.svg"
          alt=""
          aria-hidden="true"
        />
      </a>

    </section>
  );
}

// ───────── TABLE OF CONTENTS ─────────
function TableOfContents({ paid, onBack, onJump, onBuy }) {
  return (
    <section className="toc" data-screen-label="02 TOC">
      <div className="toc__clouds" aria-hidden="true">
        <span className="toc__cloud toc__cloud--one" />
        <span className="toc__cloud toc__cloud--two" />
        <span className="toc__cloud toc__cloud--three" />
        <span className="toc__cloud toc__cloud--four" />
        <span className="toc__cloud toc__cloud--five" />
        <span className="toc__cloud toc__cloud--six" />
      </div>

      <img
        className="toc__balloon"
        src="/icons/book-web-icons/doodle-hot-air-balloon.svg"
        alt=""
        aria-hidden="true"
      />

      <header className="topbar topbar--toc">
        <button className="topbar__back" onClick={onBack} aria-label="Назад">
          <span className="topbar__back-arrow" aria-hidden="true" />
        </button>
        <div className="topbar__title topbar__title--bookname">
          <img
            className="topbar__bookname"
            src="/icons/book-web-icons/bookname.svg"
            alt="Больше не буду меньше"
          />
        </div>
        <div className="topbar__right">
          <span className="welcome-nav__link toc__current-nav" aria-current="page">
            Оглавление
          </span>
          <button className="welcome-nav__link site-buy-button toc__top-buy" onClick={onBuy}>
            Купить — {NAV_PRICE}
          </button>
        </div>
      </header>

      <main className="toc__main">
        <div className="toc__paper">
          <div className="toc__intro">
            <p className="toc__intro-sub">
              Первую главу можно прочитать бесплатно.<br />
              Остальные открываются в полной книге.
            </p>
          </div>

          <ol className="toc__list">
            {CHAPTERS.map((ch) => {
              const hasPage = typeof ch.firstPage === 'number';
              const locked = !ch.free && !paid;
              const available = hasPage && (ch.free || paid);
              const unavailable = !hasPage && paid;
              const rowClassName = [
                'toc-row',
                ch.free ? 'toc-row--free' : '',
                available ? 'toc-row--available' : '',
                locked ? 'toc-row--locked' : '',
                unavailable ? 'toc-row--unavailable' : '',
              ].filter(Boolean).join(' ');

              const handleChapterClick = () => {
                if (available) onJump(ch.firstPage);
                else if (locked) onBuy();
              };

              return (
                <li key={ch.num} className={rowClassName}>
                  <button
                    className="toc-row__btn"
                    disabled={unavailable}
                    onClick={handleChapterClick}
                    aria-label={`Глава ${Number(ch.num)} ${ch.title}${locked ? ' — доступно в полной книге' : ''}`}
                  >
                    <span className="toc-row__num">Глава {Number(ch.num)}</span>
                    <span className="toc-row__title">{ch.title}</span>
                    <span className="toc-row__leader" aria-hidden="true" />
                    <span className="toc-row__page">
                      {ch.page ? <>с.&nbsp;{String(ch.page).padStart(2, '0')}</> : null}
                    </span>
                    <span className="toc-row__action" aria-hidden="true">
                      {available
                        ? <span className="toc-row__arrow">→</span>
                        : <span className="toc-row__lock"><LockIcon /></span>
                      }
                    </span>
                  </button>
                </li>
              );
            })}
          </ol>
        </div>
      </main>
    </section>
  );
}

function LockIcon() {
  return (
    <svg width="11" height="13" viewBox="0 0 11 13" fill="none" aria-hidden="true">
      <rect x="0.6" y="5.5" width="9.8" height="6.9" rx="0.4" stroke="currentColor" strokeWidth="0.9" fill="none"/>
      <path d="M2.6 5.5V3.4a2.9 2.9 0 0 1 5.8 0v2.1" stroke="currentColor" strokeWidth="0.9" fill="none"/>
    </svg>
  );
}

// ───────── READER ─────────
// Build spread list for desktop: pair pages starting at index 1 (dedication)
// Spreads: [2,3],[4,5],[6,7],[8,9],[10,11], PAYWALL, [12,13], ...
function buildSpreads() {
  const out = [];
  // first spread shows cover alone on the right
  out.push({ kind: 'cover', left: null, right: PAGES[0] });
  // pair from dedication onward
  for (let i = 1; i < PAGES.length; i += 2) {
    const left = PAGES[i] || null;
    const right = PAGES[i + 1] || null;
    out.push({ kind: 'spread', left, right });
    // after the spread containing page 11, insert paywall
    if ((left && left.n === LAST_FREE_PAGE) || (right && right.n === LAST_FREE_PAGE)) {
      out.push({ kind: 'paywall' });
    }
  }
  return out;
}

const SPREADS = buildSpreads();

// For mobile: page-by-page with paywall inserted after page 11
function buildMobileSequence() {
  const out = [];
  for (const p of PAGES) {
    out.push({ kind: 'page', page: p });
    if (p.n === LAST_FREE_PAGE) out.push({ kind: 'paywall' });
  }
  return out;
}
const MOBILE_SEQ = buildMobileSequence();

function Reader({ paid, startPage, onToc, onBuy, onBack, onProgress, sync, onSync }) {
  // pageNumber-based current position. Convert to spread index / mobile index.
  const [currentPage, setCurrentPage] = useState(startPage || 2);
  const [direction, setDirection] = useState('next');
  const [isMobile, setIsMobile] = useState(false);
  const [chromeOpen, setChromeOpen] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const stageRef = useRef(null);
  const chromeTimerRef = useRef(null);

  const openChrome = useCallback(() => {
    if (chromeTimerRef.current) {
      window.clearTimeout(chromeTimerRef.current);
      chromeTimerRef.current = null;
    }
    setChromeOpen(true);
  }, []);

  const scheduleChromeClose = useCallback(() => {
    if (chromeTimerRef.current) {
      window.clearTimeout(chromeTimerRef.current);
    }

    chromeTimerRef.current = window.setTimeout(() => {
      setChromeOpen(false);
      chromeTimerRef.current = null;
    }, 260);
  }, []);

  const handleReaderMouseMove = useCallback((event) => {
    if (event.clientY <= 92) {
      openChrome();
      return;
    }

    if (chromeOpen && event.clientY > 132) {
      scheduleChromeClose();
    }
  }, [chromeOpen, openChrome, scheduleChromeClose]);

  useEffect(() => {
    return () => {
      if (chromeTimerRef.current) {
        window.clearTimeout(chromeTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const mq = window.matchMedia('(max-width: 1100px)');
    const upd = () => setIsMobile(mq.matches);
    upd();
    mq.addEventListener('change', upd);
    return () => mq.removeEventListener('change', upd);
  }, []);

  useEffect(() => {
    setCurrentPage(startPage || 2);
  }, [startPage]);

  useEffect(() => {
    onProgress?.(currentPage);
  }, [currentPage, onProgress]);

  // Find the spread index containing currentPage
  const spreadIndex = useMemo(() => {
    if (currentPage === 0) return 0; // paywall sentinel
    for (let i = 0; i < SPREADS.length; i++) {
      const s = SPREADS[i];
      if (s.kind === 'paywall') continue;
      if ((s.left && s.left.n === currentPage) || (s.right && s.right.n === currentPage)) return i;
    }
    return 0;
  }, [currentPage]);

  const mobileIndex = useMemo(() => {
    if (currentPage === 0) return MOBILE_SEQ.findIndex(s => s.kind === 'paywall');
    return MOBILE_SEQ.findIndex(s => s.kind === 'page' && s.page.n === currentPage);
  }, [currentPage]);

  const activeSpread = SPREADS[spreadIndex];
  const canGoPrev = isMobile ? mobileIndex > 0 : spreadIndex > 0;

  useEffect(() => {
    if (paid && showPaywall) setShowPaywall(false);
  }, [paid, showPaywall]);

  useEffect(() => {
    if (!paid && currentPage === 0) {
      setCurrentPage(LAST_FREE_PAGE);
      setShowPaywall(true);
    }
    if (!paid && currentPage >= FIRST_PAID_PAGE) {
      setCurrentPage(LAST_FREE_PAGE);
      setShowPaywall(true);
    }
  }, [paid, currentPage]);

  const openChapterEndModal = useCallback(() => {
    setCurrentPage(LAST_FREE_PAGE);
    setShowPaywall(true);
  }, []);

  const next = useCallback(() => {
    setDirection('next');
    if (isMobile) {
      let idx = mobileIndex + 1;
      if (idx >= MOBILE_SEQ.length) return;
      let s = MOBILE_SEQ[idx];
      if (s.kind === 'paywall') {
        if (!paid) { openChapterEndModal(); return; }
        idx += 1;
        if (idx >= MOBILE_SEQ.length) return;
        s = MOBILE_SEQ[idx];
      }
      // skip locked pages if not paid
      if (!paid && s.page.n >= FIRST_PAID_PAGE) { openChapterEndModal(); return; }
      setCurrentPage(s.page.n);
    } else {
      let idx = spreadIndex + 1;
      if (idx >= SPREADS.length) return;
      let s = SPREADS[idx];
      if (s.kind === 'paywall') {
        if (!paid) { openChapterEndModal(); return; }
        idx += 1;
        if (idx >= SPREADS.length) return;
        s = SPREADS[idx];
      }
      const firstN = (s.left || s.right).n;
      if (!paid && firstN >= FIRST_PAID_PAGE) { openChapterEndModal(); return; }
      setCurrentPage(firstN);
    }
  }, [isMobile, mobileIndex, spreadIndex, paid, openChapterEndModal]);

  const prev = useCallback(() => {
    setDirection('prev');
    if (currentPage === 0) {
      // currently on paywall; go back to last free page
      setShowPaywall(false);
      setCurrentPage(LAST_FREE_PAGE);
      return;
    }
    if (isMobile) {
      let idx = mobileIndex - 1;
      if (idx < 0) return;
      let s = MOBILE_SEQ[idx];
      if (s.kind === 'paywall') {
        idx -= 1;
        if (idx < 0) return;
        s = MOBILE_SEQ[idx];
      }
      setCurrentPage(s.page.n);
    } else {
      let idx = spreadIndex - 1;
      if (idx < 0) return;
      let s = SPREADS[idx];
      if (s.kind === 'paywall') {
        idx -= 1;
        if (idx < 0) return;
        s = SPREADS[idx];
      }
      const firstN = (s.left || s.right).n;
      setCurrentPage(firstN);
    }
  }, [isMobile, mobileIndex, spreadIndex, currentPage]);

  // Keyboard nav
  useEffect(() => {
    const onKey = (e) => {
      if (showPaywall) {
        if (e.key === 'Escape') {
          e.preventDefault();
          setShowPaywall(false);
        } else if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === 'ArrowLeft' || e.key === 'PageUp') {
          e.preventDefault();
        }
        return;
      }
      if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); next(); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prev(); }
      else if (e.key === 'Escape') onBack && onBack();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [next, prev, onBack, showPaywall]);

  // Progress for display
  const progressPage = currentPage === 0 ? LAST_FREE_PAGE : currentPage;
  const progressMax = paid ? TOTAL_PAGES : LAST_FREE_PAGE;
  const progressDenom = paid ? TOTAL_PAGES : LAST_FREE_PAGE;
  const progressPct = Math.min(100, (progressPage / progressDenom) * 100);

  const currentChapter = useMemo(() => {
    const ch = CHAPTERS.find(c =>
      typeof c.firstPage === 'number' &&
      currentPage >= c.firstPage &&
      currentPage < c.firstPage + c.pages
    );
    return ch || CHAPTERS[0];
  }, [currentPage]);

  return (
    <section
      className="reader"
      data-screen-label="03 Reader"
      onMouseLeave={scheduleChromeClose}
      onMouseMove={handleReaderMouseMove}
    >
      <div className="reader__hover-zone" aria-hidden="true" onMouseEnter={openChrome} />

      <div
        className={`reader__chrome ${chromeOpen ? 'is-open' : ''}`}
        onBlur={scheduleChromeClose}
        onFocus={openChrome}
        onMouseEnter={openChrome}
        onMouseLeave={scheduleChromeClose}
      >
        <header className="topbar topbar--reader">
          <button className="topbar__back" onClick={onBack} aria-label="На главную">
            <span className="topbar__back-arrow" aria-hidden="true" />
          </button>

          <div className="topbar__title">
            <span className="topbar__title-eyebrow">Глава {currentChapter.num}</span>
            <span className="topbar__title-main">{currentChapter.title}</span>
          </div>

          <div className="topbar__right">
            <SyncControl sync={sync} onClick={onSync} />
            <div className="reader__primary-nav">
              <button className="welcome-nav__link" onClick={onToc}>Оглавление</button>
              <button className="welcome-nav__link site-buy-button" onClick={onBuy}>
                Купить — {NAV_PRICE}
              </button>
            </div>
          </div>
        </header>

        <div className="reader__progress" aria-hidden="true">
          <div className="reader__progress-bar" style={{ width: `${progressPct}%` }} />
          <div className="reader__progress-ticks">
            {CHAPTERS.filter((ch) => typeof ch.firstPage === 'number').map((ch) => (
              <div key={ch.num} className="reader__progress-tick" style={{ left: `${(ch.firstPage / progressDenom) * 100}%` }} />
            ))}
          </div>
        </div>
      </div>

      <main className="reader__stage" ref={stageRef}>
        {isMobile ? (
          <div className={`reader__mobile reader__mobile--${direction}`} key={`m-${currentPage}`}>
            <BookPage page={MOBILE_SEQ[mobileIndex]?.page} />
          </div>
        ) : (
          <div className={`reader__spread reader__spread--${direction}`} key={spreadIndex}>
            <div className="reader__page-slot reader__page-slot--left">
              <BookPage page={activeSpread?.left} />
            </div>
            <div className="reader__page-slot reader__page-slot--right">
              <BookPage page={activeSpread?.right} />
            </div>
          </div>
        )}

        {canGoPrev && (
          <button className="reader__nav reader__nav--prev" onClick={prev} aria-label="Назад">
            <svg width="34" height="34" viewBox="0 0 34 34" fill="none" aria-hidden="true">
              <path d="M21 10 12 17l9 7" stroke="currentColor" strokeWidth="1.15" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}
        <button className="reader__nav reader__nav--next" onClick={next} aria-label="Вперёд">
          <svg width="34" height="34" viewBox="0 0 34 34" fill="none" aria-hidden="true">
            <path d="M13 10l9 7-9 7" stroke="currentColor" strokeWidth="1.15" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </main>

      {showPaywall && !paid && (
        <ChapterEndModal
          onClose={() => setShowPaywall(false)}
          onToc={() => {
            setShowPaywall(false);
            onToc();
          }}
          onBuy={() => {
            setShowPaywall(false);
            onBuy();
          }}
        />
      )}
    </section>
  );
}

function ChapterEndModal({ onClose, onBuy, onToc }) {
  return (
    <div className="modal chapter-gate" data-screen-label="04 Chapter End Modal" role="dialog" aria-modal="true">
      <div className="modal__backdrop" onClick={onClose} />
      <div className="modal__sheet chapter-gate__sheet">
        <button className="modal__close" onClick={onClose} aria-label="Закрыть">
          <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
            <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" strokeWidth="1.2"/>
          </svg>
        </button>

        <div className="modal__eyebrow">Первая глава закончилась</div>
        <h3 className="modal__title">Чтобы продолжить чтение, нужно купить книгу</h3>
        <p className="modal__sub">Первая глава открыта бесплатно. Дальше доступно после покупки полной цифровой книги.</p>

        <div className="chapter-gate__actions">
          <button className="btn btn--primary" onClick={onBuy}>Купить книгу — {PRICE}</button>
          <button className="link link--soft" onClick={onToc}>Вернуться к оглавлению</button>
        </div>
      </div>
    </div>
  );
}

// ───────── PAYWALL ─────────
function PaywallScreen({ onBuy, onToc, embedded }) {
  return (
    <div className={`paywall ${embedded ? 'paywall--embedded' : ''}`} data-screen-label="04 Paywall">
      <div className="paywall__sheet">
        <div className="paywall__ornament" aria-hidden="true">
          <span className="paywall__ornament-line" />
          <span className="paywall__ornament-dot" />
          <span className="paywall__ornament-line" />
        </div>
        <div className="paywall__eyebrow">Конец первой главы</div>
        <h2 className="paywall__title">Дальше&nbsp;— вся книга</h2>
        <p className="paywall__lede">
          Первая глава открыта. Полная цифровая книга стоит {PRICE} и&nbsp;открывает доступ ко&nbsp;всем главам.
        </p>

        <ul className="paywall__list">
          <li><span className="paywall__dot" />Все четыре главы и&nbsp;послесловие</li>
          <li><span className="paywall__dot" />Чтение с&nbsp;телефона и&nbsp;компьютера</li>
          <li><span className="paywall__dot" />Сохранение прогресса</li>
        </ul>

        <div className="paywall__price">
          <span className="paywall__price-key">Цена</span>
          <span className="paywall__price-val">{PRICE}</span>
        </div>

        <div className="paywall__actions">
          <button className="btn btn--primary" onClick={onBuy}>
            <span>Купить полную книгу за {PRICE}</span>
          </button>
          <button className="link link--soft" onClick={onToc}>Вернуться к оглавлению</button>
        </div>
      </div>
    </div>
  );
}

// ───────── PURCHASE MODAL ─────────
function PurchaseModal({ onClose, onPaid }) {
  const [step, setStep] = useState('form'); // form -> processing -> done
  const [card, setCard] = useState('');
  const [exp, setExp] = useState('');
  const [cvv, setCvv] = useState('');

  const submit = (e) => {
    e.preventDefault();
    setStep('processing');
    setTimeout(() => {
      setStep('done');
      setTimeout(() => onPaid(), 900);
    }, 1200);
  };

  return (
    <div className="modal" data-screen-label="05 Purchase" role="dialog" aria-modal="true">
      <div className="modal__backdrop" onClick={onClose} />
      <div className="modal__sheet">
        <button className="modal__close" onClick={onClose} aria-label="Закрыть">
          <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
            <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" strokeWidth="1.2"/>
          </svg>
        </button>

        {step !== 'done' && (
          <>
            <div className="modal__eyebrow">Покупка</div>
            <h3 className="modal__title">Полная цифровая книга</h3>
            <p className="modal__sub">Доступ ко&nbsp;всем главам, чтение с&nbsp;телефона и&nbsp;компьютера, сохранение прогресса.</p>

            <div className="modal__product">
              <div className="modal__product-row">
                <span className="modal__product-name">«Больше не буду меньше»</span>
                <span className="modal__product-price">{PRICE}</span>
              </div>
              <div className="modal__product-meta">
                <span>Саша Довгополова</span>
                <span className="modal__product-sep">·</span>
                <span>{TOTAL_PAGES} страниц</span>
                <span className="modal__product-sep">·</span>
                <span>4 главы</span>
              </div>
            </div>

            <form className="modal__form" onSubmit={submit}>
              <label className="field">
                <span className="field__label">Номер карты</span>
                <input
                  className="field__input"
                  inputMode="numeric"
                  placeholder="0000  0000  0000  0000"
                  value={card}
                  onChange={(e) => setCard(e.target.value.replace(/[^\d ]/g, '').slice(0, 19))}
                  required
                />
              </label>
              <div className="field-row">
                <label className="field">
                  <span className="field__label">Срок</span>
                  <input
                    className="field__input"
                    placeholder="MM/ГГ"
                    value={exp}
                    onChange={(e) => setExp(e.target.value.replace(/[^\d/]/g, '').slice(0,5))}
                    required
                  />
                </label>
                <label className="field">
                  <span className="field__label">CVV</span>
                  <input
                    className="field__input"
                    placeholder="•••"
                    type="password"
                    value={cvv}
                    onChange={(e) => setCvv(e.target.value.replace(/\D/g, '').slice(0,3))}
                    required
                  />
                </label>
              </div>

              <button className="btn btn--primary btn--block" type="submit" disabled={step==='processing'}>
                {step === 'processing'
                  ? <span className="btn__processing">Обрабатываем платёж…</span>
                  : <span>Оплатить {PRICE} и&nbsp;продолжить чтение</span>}
              </button>
            </form>

            <div className="modal__legal">
              Это демо-оплата. После нажатия книга откроется полностью.
            </div>
          </>
        )}

        {step === 'done' && (
          <div className="modal__success">
            <div className="modal__success-mark" aria-hidden="true">
              <svg width="34" height="26" viewBox="0 0 34 26" fill="none">
                <path d="M2 13l10 10L32 3" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="square"/>
              </svg>
            </div>
            <div className="modal__success-title">Книга открыта</div>
            <div className="modal__success-sub">Возвращаем к&nbsp;чтению…</div>
          </div>
        )}
      </div>
    </div>
  );
}

function SyncModal({
  configured,
  user,
  syncStatus,
  syncError,
  onClose,
  onSendMagicLink,
  onSignOut,
}) {
  const [email, setEmail] = useState(user?.email || '');
  const [requestState, setRequestState] = useState('idle');
  const [requestError, setRequestError] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setRequestState('sending');
    setRequestError('');

    try {
      await onSendMagicLink(email.trim());
      setRequestState('sent');
    } catch (error) {
      setRequestError(error.message || 'Не удалось отправить письмо.');
      setRequestState('error');
    }
  };

  const logout = async () => {
    setRequestError('');
    try {
      await onSignOut();
      onClose();
    } catch (error) {
      setRequestError(error.message || 'Не удалось выйти.');
    }
  };

  return (
    <div className="modal sync-modal" role="dialog" aria-modal="true">
      <div className="modal__backdrop" onClick={onClose} />
      <div className="modal__sheet sync-modal__sheet">
        <button className="modal__close" onClick={onClose} aria-label="Закрыть">
          <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
            <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" strokeWidth="1.2"/>
          </svg>
        </button>

        <div className="modal__eyebrow">Прогресс чтения</div>

        {!configured ? (
          <>
            <h3 className="modal__title">Прогресс хранится на этом устройстве</h3>
            <p className="modal__sub">
              Облачная синхронизация станет доступна после подключения Supabase.
            </p>
          </>
        ) : user ? (
          <>
            <h3 className="modal__title">Чтение синхронизировано</h3>
            <p className="modal__sub">
              Продолжить с&nbsp;этой страницы можно на любом устройстве после входа.
            </p>
            <div className="sync-account">
              <span className="sync-account__email">{user.email}</span>
              <span className={`sync-account__status sync-account__status--${syncStatus}`}>
                {syncStatus === 'saving'
                  ? 'Сохраняем последнюю страницу…'
                  : syncStatus === 'error'
                  ? 'Не удалось синхронизировать'
                  : 'Последняя страница сохранена'}
              </span>
            </div>
            <button className="link link--soft" onClick={logout}>Выйти на этом устройстве</button>
          </>
        ) : requestState === 'sent' ? (
          <>
            <h3 className="modal__title">Письмо отправлено</h3>
            <p className="modal__sub">
              Откройте ссылку в&nbsp;письме. После входа текущая страница сохранится автоматически.
            </p>
            <button className="btn btn--primary btn--block" onClick={onClose}>
              Хорошо
            </button>
          </>
        ) : (
          <>
            <h3 className="modal__title">Продолжить на другом устройстве</h3>
            <p className="modal__sub">
              Введите email — мы пришлём ссылку для входа без пароля.
            </p>
            <form className="modal__form" onSubmit={submit}>
              <label className="field">
                <span className="field__label">Email</span>
                <input
                  className="field__input"
                  type="email"
                  autoComplete="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </label>
              <button
                className="btn btn--primary btn--block"
                type="submit"
                disabled={requestState === 'sending'}
              >
                {requestState === 'sending' ? 'Отправляем…' : 'Получить ссылку'}
              </button>
            </form>
          </>
        )}

        {(requestError || syncError) && (
          <p className="sync-modal__error">{requestError || syncError}</p>
        )}
      </div>
    </div>
  );
}

// ───────── APP ─────────
function App() {
  const initialStateRef = useRef(readLocalState());
  const [view, setView] = useState('welcome');
  const [paid, setPaid] = useState(initialStateRef.current.paid);
  const [readerStart, setReaderStart] = useState(initialStateRef.current.lastPage);
  const [progressUpdatedAt, setProgressUpdatedAt] = useState(
    initialStateRef.current.updatedAt,
  );
  const [showPurchase, setShowPurchase] = useState(false);
  const [showSync, setShowSync] = useState(false);
  const [showIntro, setShowIntro] = useState(() => {
    try {
      return localStorage.getItem(INTRO_STORAGE_KEY) !== 'true';
    } catch (e) {
      return true;
    }
  });
  const hasFullAccess = paid || PREVIEW_ALL_CHAPTERS;

  const readerStartRef = useRef(readerStart);
  const progressUpdatedAtRef = useRef(progressUpdatedAt);

  const updateProgress = useCallback((page, timestamp = Date.now(), force = false) => {
    const nextPage = Math.min(TOTAL_PAGES, Math.max(1, Math.round(page || 2)));

    if (!force && readerStartRef.current === nextPage) return;

    readerStartRef.current = nextPage;
    progressUpdatedAtRef.current = timestamp;
    setReaderStart(nextPage);
    setProgressUpdatedAt(timestamp);
  }, []);

  const applyRemoteProgress = useCallback((page, timestamp) => {
    updateProgress(page, timestamp, true);
  }, [updateProgress]);

  const applyCloudEntitlement = useCallback(() => {
    setPaid(true);
  }, []);

  const sync = useReadingSync({
    page: readerStart,
    updatedAt: progressUpdatedAt,
    onRemoteProgress: applyRemoteProgress,
    onCloudEntitlement: applyCloudEntitlement,
  });

  // Persist
  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          paid,
          lastPage: readerStart,
          updatedAt: progressUpdatedAt,
        }),
      );
    } catch (e) {}
  }, [paid, readerStart, progressUpdatedAt]);

  const openReader = (page) => {
    updateProgress(page || readerStart || 2);
    setView('reader');
  };

  const onBuy = () => setShowPurchase(true);
  const onPaid = () => {
    setPaid(true);
    setShowPurchase(false);
    // jump into chapter 2
    updateProgress(FIRST_PAID_PAGE);
    setView('reader');
  };

  const finishIntro = () => {
    setShowIntro(false);
    setView('welcome');
  };

  return (
    <div className="app" data-paid={hasFullAccess}>
      {showIntro ? (
        <IntroPreview onDone={finishIntro} />
      ) : (
        <>
          {view === 'welcome' && (
            <Welcome
              paid={hasFullAccess}
              onOpen={() => openReader(readerStart)}
              onToc={() => setView('toc')}
              onBuy={onBuy}
              sync={sync}
              onSync={() => setShowSync(true)}
            />
          )}
          {view === 'toc' && (
            <TableOfContents
              paid={paid}
              onBack={() => setView('welcome')}
              onJump={(p) => openReader(p)}
              onBuy={onBuy}
            />
          )}
          {view === 'reader' && (
            <Reader
              paid={hasFullAccess}
              startPage={readerStart}
              onToc={() => setView('toc')}
              onBuy={onBuy}
              onBack={() => setView('welcome')}
              onProgress={updateProgress}
              sync={sync}
              onSync={() => setShowSync(true)}
            />
          )}
          {view === 'paywall' && (
            <div className="paywall-fullscreen" data-screen-label="04 Paywall">
              <header className="topbar">
                <button className="topbar__back" onClick={() => setView('reader')}>
                  <svg width="22" height="10" viewBox="0 0 22 10" fill="none" aria-hidden="true">
                    <path d="M22 5H2M6 1L2 5l4 4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="square" fill="none"/>
                  </svg>
                  <span>К чтению</span>
                </button>
                <div className="topbar__title">
                  <span className="topbar__title-eyebrow">Граница книги</span>
                  <span className="topbar__title-main">Paywall</span>
                </div>
                <div className="topbar__right">
                  <button className="link link--quiet" onClick={() => setView('toc')}>Оглавление</button>
                </div>
              </header>
              <PaywallScreen onBuy={onBuy} onToc={() => setView('toc')} />
            </div>
          )}
          {view === 'purchase' && (
            <div className="purchase-fullscreen" data-screen-label="05 Purchase">
              <header className="topbar">
                <button className="topbar__back" onClick={() => setView('welcome')}>
                  <svg width="22" height="10" viewBox="0 0 22 10" fill="none" aria-hidden="true">
                    <path d="M22 5H2M6 1L2 5l4 4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="square" fill="none"/>
                  </svg>
                  <span>Назад</span>
                </button>
                <div className="topbar__title">
                  <span className="topbar__title-eyebrow">Покупка</span>
                  <span className="topbar__title-main">Полная цифровая книга</span>
                </div>
                <div className="topbar__right"></div>
              </header>
              <div className="purchase-inline">
                <PurchaseModal onClose={() => setView('welcome')} onPaid={onPaid} />
              </div>
            </div>
          )}

          {showPurchase && (
            <PurchaseModal onClose={() => setShowPurchase(false)} onPaid={onPaid} />
          )}

          {showSync && (
            <SyncModal
              configured={sync.configured}
              user={sync.user}
              syncStatus={sync.syncStatus}
              syncError={sync.syncError}
              onClose={() => setShowSync(false)}
              onSendMagicLink={sync.sendMagicLink}
              onSignOut={sync.signOut}
            />
          )}
        </>
      )}

    </div>
  );
}

// Mount
const root = createRoot(document.getElementById('root'));
root.render(<App />);
