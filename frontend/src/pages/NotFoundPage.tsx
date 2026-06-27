import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center px-4 py-32 text-center">
      <p className="text-7xl font-bold text-blue-600">404</p>
      <h1 className="mt-4 text-2xl font-bold text-foreground">Страница не найдена</h1>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        Возможно, ссылка устарела или страница была перемещена.
      </p>
      <Button className="mt-8" render={<Link to="/" />}>
        На главную
      </Button>
    </div>
  )
}
