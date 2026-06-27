export function Footer() {
  return (
    <footer className="mt-auto border-t border-border bg-muted/30">
      <div className="mx-auto max-w-7xl px-4 py-6 text-center text-sm text-muted-foreground">
        <p>
          Цены актуальны в течение 30 дней с момента обновления. Всегда уточняйте стоимость
          в клинике перед визитом.
        </p>
        <p className="mt-1 text-xs">© {new Date().getFullYear()} MedServicePrice.kz</p>
      </div>
    </footer>
  )
}
