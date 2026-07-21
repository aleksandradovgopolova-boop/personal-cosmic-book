export const products = {
  basic: {
    id: "pcb_basic",
    title: "Полная книга",
    priceRub: 990
  },
  gift: {
    id: "pcb_bundle",
    title: "Подарочная книга",
    priceRub: 990
  },
  compatibility: {
    id: "pcb_compatibility",
    title: "Книга пары",
    priceRub: 1490
  }
} as const;

// The book has exactly 10 sections (see book-structure-10-sections.md).
export const paidBookSections = [
  { id: "01_main_theme", title: "Главная тема твоей книги" },
  { id: "02_inner_world", title: "Твой внутренний мир" },
  { id: "03_strengths", title: "Твои сильные стороны" },
  { id: "04_inner_tensions", title: "Внутренние противоречия" },
  { id: "05_love", title: "Любовь и близость" },
  { id: "06_realization", title: "Реализация, дело и деньги" },
  { id: "07_outer_expression", title: "Как ты проявляешься в мире" },
  { id: "08_life_patterns", title: "Повторяющиеся сценарии и точки роста" },
  { id: "09_personal_formula", title: "Твоя персональная формула" },
  { id: "10_next_chapter", title: "Твой следующий шаг" }
] as const;

// The four fixed elemental themes (see design-system-elements-v2.md).
export const bookThemes = [
  { id: "earth", label: "Земля · Корни", hint: "спокойное и собранное оформление" },
  { id: "water", label: "Вода · Глубина", hint: "мягкое и глубокое оформление" },
  { id: "air", label: "Воздух · Дыхание", hint: "светлое и просторное оформление" },
  { id: "fire", label: "Огонь · Искра", hint: "тёплое и выразительное оформление" }
] as const;
