import { products } from "@/lib/products";

export default function Home() {
  return (
    <main className="landing">
      <section className="landing-hero">
        <p className="landing-kicker">Personal Cosmic Book</p>
        <h1>Персональная книга на основе твоей натальной карты</h1>
        <p className="landing-lead">
          Полная книга для себя и подарочная книга для близкого человека.
          Расчёт карты, синтез паттернов и генерация текста — в одном сервисе.
        </p>
      </section>

      <section className="landing-products" aria-label="Продукты">
        {Object.values(products).map((product) => (
          <article key={product.id} className="landing-card">
            <h2>{product.title}</h2>
            <p className="landing-price">{product.priceRub} ₽</p>
          </article>
        ))}
      </section>
    </main>
  );
}
