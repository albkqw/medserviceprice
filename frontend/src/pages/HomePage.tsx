import { FlaskConical, Stethoscope, Activity } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { SearchBar } from '@/features/search/components/SearchBar'
import { config } from '@/lib/config'

const POPULAR_CATEGORIES = [
  {
    icon: <FlaskConical className="h-6 w-6" />,
    label: 'Анализы крови',
    query: 'анализ крови',
  },
  {
    icon: <Stethoscope className="h-6 w-6" />,
    label: 'Приём терапевта',
    query: 'терапевт',
  },
  {
    icon: <Activity className="h-6 w-6" />,
    label: 'УЗИ',
    query: 'узи',
  },
]

export function HomePage() {
  const navigate = useNavigate()

  function handleSearch(query: string, citySlug: string) {
    navigate(`/search?q=${encodeURIComponent(query)}&city=${citySlug}`)
  }

  return (
    <div>
      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-background px-4 py-24 text-center">
        <div className="mb-3 inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
          Казахстан · Алматы, Астана, Шымкент
        </div>

        <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Сравните цены на
          <br />
          <span className="text-blue-600">медицинские услуги</span>
        </h1>

        <p className="mt-4 max-w-xl text-base text-muted-foreground sm:text-lg">
          {config.appName} — находим лучшую цену на анализы и услуги в клиниках вашего
          города. Как Aviasales, только для медицины.
        </p>

        <div className="mt-8 w-full max-w-2xl px-4">
          <SearchBar size="hero" onSearch={handleSearch} />
        </div>

        <p className="mt-3 text-xs text-muted-foreground">
          Более 27 000 актуальных цен из 645 клиник
        </p>
      </section>

      {/* Popular categories */}
      <section className="mx-auto max-w-7xl px-4 py-12">
        <h2 className="mb-6 text-lg font-semibold text-foreground">Популярные запросы</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {POPULAR_CATEGORIES.map(({ icon, label, query }) => (
            <button
              key={query}
              onClick={() => navigate(`/search?q=${encodeURIComponent(query)}`)}
              className="flex items-center gap-3 rounded-lg border border-border bg-card p-4 text-left transition-shadow hover:shadow-md hover:border-blue-200"
            >
              <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                {icon}
              </span>
              <span className="text-sm font-medium text-foreground">{label}</span>
            </button>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-muted/30 px-4 py-12">
        <div className="mx-auto max-w-7xl">
          <h2 className="mb-8 text-center text-lg font-semibold text-foreground">
            Как это работает
          </h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            {[
              {
                step: '1',
                title: 'Введите услугу',
                desc: 'Введите название анализа или услуги. Система автоматически подберёт совпадения.',
              },
              {
                step: '2',
                title: 'Выберите город',
                desc: 'Укажите город, чтобы видеть только актуальные предложения рядом с вами.',
              },
              {
                step: '3',
                title: 'Сравните цены',
                desc: 'Смотрите цены из разных клиник, отсортированные от дешёвых к дорогим.',
              },
            ].map(({ step, title, desc }) => (
              <div key={step} className="flex gap-4">
                <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
                  {step}
                </span>
                <div>
                  <p className="font-semibold text-foreground">{title}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
