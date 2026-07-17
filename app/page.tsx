"use client";

import Image from "next/image";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { CSSProperties } from "react";

type Spread = {
  title: string;
  label: string;
  src: string;
  width: number;
  height: number;
};

const spreads: Spread[] = [
  {
    title: "Больше не буду меньше",
    label: "Обложка",
    src: "/book-spreads/spread-01.png",
    width: 709,
    height: 1024
  },
  {
    title: "Посвящение",
    label: "Для семьи",
    src: "/book-spreads/spread-02.png",
    width: 709,
    height: 1024
  },
  {
    title: "У самурая свой путь",
    label: "Глава 01",
    src: "/book-spreads/spread-03.png",
    width: 1024,
    height: 740
  },
  {
    title: "У самурая свой путь",
    label: "Разворот 01.1",
    src: "/book-spreads/spread-04.png",
    width: 1024,
    height: 740
  },
  {
    title: "У самурая свой путь",
    label: "Разворот 01.2",
    src: "/book-spreads/spread-05.png",
    width: 1024,
    height: 740
  },
  {
    title: "У самурая свой путь",
    label: "Разворот 01.3",
    src: "/book-spreads/spread-06.png",
    width: 1024,
    height: 740
  },
  {
    title: "У самурая свой путь",
    label: "Разворот 01.4",
    src: "/book-spreads/spread-07.png",
    width: 1024,
    height: 740
  },
  {
    title: "Вывернуть наизнанку",
    label: "Глава 02",
    src: "/book-spreads/spread-08.png",
    width: 1024,
    height: 740
  },
  {
    title: "Вывернуть наизнанку",
    label: "Разворот 02.1",
    src: "/book-spreads/spread-09.png",
    width: 1024,
    height: 740
  },
  {
    title: "Вывернуть наизнанку",
    label: "Разворот 02.2",
    src: "/book-spreads/spread-10.png",
    width: 1024,
    height: 740
  },
  {
    title: "Вывернуть наизнанку",
    label: "Разворот 02.3",
    src: "/book-spreads/spread-11.png",
    width: 1024,
    height: 740
  },
  {
    title: "Вывернуть наизнанку",
    label: "Разворот 02.4",
    src: "/book-spreads/spread-12.png",
    width: 1024,
    height: 740
  },
  {
    title: "Счастливый билетик",
    label: "Глава 03",
    src: "/book-spreads/spread-13.png",
    width: 1024,
    height: 740
  },
  {
    title: "Счастливый билетик",
    label: "Разворот 03.1",
    src: "/book-spreads/spread-14.png",
    width: 1024,
    height: 740
  },
  {
    title: "Счастливый билетик",
    label: "Разворот 03.2",
    src: "/book-spreads/spread-15.png",
    width: 1024,
    height: 740
  },
  {
    title: "Счастливый билетик",
    label: "Разворот 03.3",
    src: "/book-spreads/spread-16.png",
    width: 1024,
    height: 740
  },
  {
    title: "Счастливый билетик",
    label: "Разворот 03.4",
    src: "/book-spreads/spread-17.png",
    width: 1024,
    height: 740
  },
  {
    title: "Чёртов борщ",
    label: "Глава 04",
    src: "/book-spreads/spread-18.png",
    width: 1024,
    height: 740
  },
  {
    title: "Чёртов борщ",
    label: "Разворот 04.1",
    src: "/book-spreads/spread-19.png",
    width: 1024,
    height: 740
  },
  {
    title: "Чёртов борщ",
    label: "Разворот 04.2",
    src: "/book-spreads/spread-20.png",
    width: 1024,
    height: 740
  },
  {
    title: "Чёртов борщ",
    label: "Разворот 04.3",
    src: "/book-spreads/spread-21.png",
    width: 1024,
    height: 740
  },
  {
    title: "Чёртов борщ",
    label: "Финальная страница",
    src: "/book-spreads/spread-22.png",
    width: 709,
    height: 1024
  }
];

const chapters = [
  { title: "Обложка", start: 0, count: 1 },
  { title: "Посвящение", start: 1, count: 1 },
  { title: "01. У самурая свой путь", start: 2, count: 5 },
  { title: "02. Вывернуть наизнанку", start: 7, count: 5 },
  { title: "03. Счастливый билетик", start: 12, count: 5 },
  { title: "04. Чёртов борщ", start: 17, count: 5 }
];

function clampIndex(index: number) {
  return Math.min(Math.max(index, 0), spreads.length - 1);
}

export default function Home() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState<"next" | "prev">("next");
  const currentSpread = spreads[currentIndex];
  const progress = useMemo(
    () => Math.round(((currentIndex + 1) / spreads.length) * 100),
    [currentIndex]
  );

  const goTo = useCallback((index: number) => {
    const nextIndex = clampIndex(index);

    if (nextIndex === currentIndex) {
      return;
    }

    setDirection(nextIndex > currentIndex ? "next" : "prev");
    setCurrentIndex(nextIndex);
  }, [currentIndex]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;

      if (target?.tagName === "INPUT" || target?.tagName === "BUTTON") {
        return;
      }

      if (event.key === "ArrowRight") {
        goTo(currentIndex + 1);
      }

      if (event.key === "ArrowLeft") {
        goTo(currentIndex - 1);
      }

      if (event.key === "Home") {
        goTo(0);
      }

      if (event.key === "End") {
        goTo(spreads.length - 1);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentIndex, goTo]);

  return (
    <main className="book-app">
      <header className="topbar">
        <button className="brand" onClick={() => goTo(0)} type="button">
          <span className="brand-mark" aria-hidden="true" />
          <span>Больше не буду меньше</span>
        </button>

        <nav className="topnav" aria-label="Навигация по книге">
          {chapters.slice(2).map((chapter) => (
            <button
              key={chapter.title}
              className={currentIndex >= chapter.start && currentIndex < chapter.start + chapter.count ? "is-active" : ""}
              onClick={() => goTo(chapter.start)}
              type="button"
            >
              {chapter.title.slice(0, 2)}
            </button>
          ))}
        </nav>
      </header>

      <div className="reader-layout">
        <aside className="toc-panel" id="contents" aria-label="Оглавление">
          <div className="toc-heading">
            <p>Оглавление</p>
            <span>{spreads.length} разворота</span>
          </div>

          <div className="chapter-list">
            {chapters.map((chapter) => (
              <button
                key={chapter.title}
                className={currentIndex >= chapter.start && currentIndex < chapter.start + chapter.count ? "chapter-link is-active" : "chapter-link"}
                onClick={() => goTo(chapter.start)}
                type="button"
              >
                <span>{chapter.title}</span>
                <small>
                  {chapter.count === 1
                    ? "1 страница"
                    : `${chapter.count} разворотов`}
                </small>
              </button>
            ))}
          </div>

          <div className="spread-strip" aria-label="Все развороты">
            {spreads.map((spread, index) => (
              <button
                key={spread.src}
                className={index === currentIndex ? "thumb-button is-current" : "thumb-button"}
                onClick={() => goTo(index)}
                style={{ "--thumb-ratio": `${spread.width} / ${spread.height}` } as CSSProperties}
                title={spread.label}
                type="button"
              >
                <Image
                  alt=""
                  height={spread.height}
                  loading="lazy"
                  sizes="(max-width: 980px) 16vw, 90px"
                  src={spread.src}
                  width={spread.width}
                />
                <span>{String(index + 1).padStart(2, "0")}</span>
              </button>
            ))}
          </div>
        </aside>

        <section className="reader-stage" aria-label="Чтение книги">
          <div className="spread-meta">
            <p>{currentSpread.label}</p>
            <h1>{currentSpread.title}</h1>
          </div>

          <div className="spread-viewport">
            <button
              className="turn-button turn-prev"
              disabled={currentIndex === 0}
              onClick={() => goTo(currentIndex - 1)}
              title="Предыдущий разворот"
              type="button"
            >
              <span aria-hidden="true">‹</span>
            </button>

            <figure
              key={currentSpread.src}
              className={`spread-frame is-${direction}`}
              style={{ "--spread-ratio": `${currentSpread.width} / ${currentSpread.height}` } as CSSProperties}
            >
              <Image
                alt={`${currentSpread.label}: ${currentSpread.title}`}
                draggable={false}
                height={currentSpread.height}
                priority={currentIndex === 0}
                sizes="(max-width: 980px) 100vw, calc(100vw - 390px)"
                src={currentSpread.src}
                width={currentSpread.width}
              />
            </figure>

            <button
              className="turn-button turn-next"
              disabled={currentIndex === spreads.length - 1}
              onClick={() => goTo(currentIndex + 1)}
              title="Следующий разворот"
              type="button"
            >
              <span aria-hidden="true">›</span>
            </button>
          </div>

          <footer className="reader-controls">
            <div className="page-count">
              <span>{String(currentIndex + 1).padStart(2, "0")}</span>
              <span>/</span>
              <span>{String(spreads.length).padStart(2, "0")}</span>
            </div>

            <label className="range-control">
              <span>{progress}%</span>
              <input
                aria-label="Позиция в книге"
                max={spreads.length - 1}
                min={0}
                onChange={(event) => goTo(Number(event.target.value))}
                type="range"
                value={currentIndex}
              />
            </label>
          </footer>
        </section>
      </div>
    </main>
  );
}
