import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Loader2 } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { CitySelect } from '@/components/common/CitySelect'
import { useServiceSuggestions } from '../hooks/useServiceSuggestions'
import { useLocalStorage } from '@/hooks/useLocalStorage'
import { cn } from '@/lib/utils'

interface SearchBarProps {
  initialQuery?: string
  initialCity?: string
  onSearch?: (query: string, citySlug: string) => void
  size?: 'default' | 'hero'
}

export function SearchBar({
  initialQuery = '',
  initialCity = '',
  onSearch,
  size = 'default',
}: SearchBarProps) {
  const navigate = useNavigate()
  const [query, setQuery] = useState(initialQuery)
  const [citySlug, setCitySlug] = useLocalStorage('lastCity', initialCity)
  const [isOpen, setIsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLUListElement>(null)

  const { data: suggestions = [], isFetching } = useServiceSuggestions(query)

  useEffect(() => {
    setQuery(initialQuery)
  }, [initialQuery])

  useEffect(() => {
    if (initialCity) setCitySlug(initialCity)
  }, [initialCity, setCitySlug])

  const showDropdown = isOpen && query.length >= 2 && suggestions.length > 0

  function handleSubmit(selectedQuery?: string) {
    const q = (selectedQuery ?? query).trim()
    if (!q || !citySlug) return
    setIsOpen(false)

    if (onSearch) {
      onSearch(q, citySlug)
    } else {
      navigate(`/search?q=${encodeURIComponent(q)}&city=${citySlug}`)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!showDropdown) {
      if (e.key === 'Enter') handleSubmit()
      return
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveIndex((i) => Math.min(i + 1, suggestions.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveIndex((i) => Math.max(i - 1, -1))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (activeIndex >= 0) {
        const selected = suggestions[activeIndex]
        setQuery(selected.name)
        setIsOpen(false)
        handleSubmit(selected.name)
      } else {
        handleSubmit()
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false)
      setActiveIndex(-1)
    }
  }

  const isHero = size === 'hero'

  return (
    <div className={cn('relative w-full', isHero && 'max-w-2xl')}>
      <div
        className={cn(
          'flex gap-2',
          isHero ? 'flex-col sm:flex-row' : 'flex-row',
        )}
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          {isFetching && (
            <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
          )}
          <Input
            ref={inputRef}
            value={query}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              setQuery(e.target.value)
              setIsOpen(true)
              setActiveIndex(-1)
            }}
            onFocus={() => setIsOpen(true)}
            onBlur={() => setTimeout(() => setIsOpen(false), 150)}
            onKeyDown={handleKeyDown}
            placeholder="Введите услугу или анализ..."
            className={cn('pl-9 pr-9', isHero && 'h-12 text-base')}
          />
        </div>

        <CitySelect
          value={citySlug}
          onChange={setCitySlug}
          className={cn(isHero && 'h-12')}
        />

        <Button
          onClick={() => handleSubmit()}
          disabled={!query.trim() || !citySlug}
          className={cn(isHero && 'h-12 px-8 text-base')}
        >
          Найти
        </Button>
      </div>

      {showDropdown && (
        <ul
          ref={listRef}
          className="absolute z-50 mt-1 w-full rounded-md border border-border bg-popover py-1 shadow-lg"
          role="listbox"
        >
          {suggestions.map((service, index) => (
            <li
              key={service.id}
              role="option"
              aria-selected={index === activeIndex}
              className={cn(
                'cursor-pointer px-4 py-2.5 text-sm',
                index === activeIndex
                  ? 'bg-accent text-accent-foreground'
                  : 'hover:bg-accent hover:text-accent-foreground',
              )}
              onMouseDown={() => {
                setQuery(service.name)
                setIsOpen(false)
                handleSubmit(service.name)
              }}
            >
              <span className="font-medium">{service.name}</span>
              <span className="ml-2 text-xs text-muted-foreground">
                {service.category === 'lab' && 'Анализ'}
                {service.category === 'doctor' && 'Приём'}
                {service.category === 'diagnostic' && 'Диагностика'}
                {service.category === 'procedure' && 'Процедура'}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
