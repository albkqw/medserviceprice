import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import type { SearchResult } from '@/types/domain'
import { SOURCE_LABELS } from '@/types/domain'
import { formatPrice } from '@/lib/formatters'

// Fix Leaflet's broken default icon paths (Vite doesn't process the PNG URLs)
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const SOURCE_COLORS: Record<string, string> = {
  kdl: '#3b82f6',      // blue-500
  invitro: '#f43f5e',  // rose-500
  doq: '#10b981',      // emerald-500
}

function makeIcon(source: string | null): L.DivIcon {
  const color = source ? (SOURCE_COLORS[source] ?? '#6366f1') : '#6366f1'
  const label = source ? (SOURCE_LABELS[source as keyof typeof SOURCE_LABELS] ?? '') : ''
  return L.divIcon({
    className: '',
    html: `
      <div style="
        background:${color};
        color:#fff;
        font-size:10px;
        font-weight:700;
        font-family:system-ui,sans-serif;
        padding:2px 5px;
        border-radius:10px;
        border:2px solid #fff;
        box-shadow:0 1px 4px rgba(0,0,0,.35);
        white-space:nowrap;
        line-height:1.4;
      ">${label}</div>`,
    iconAnchor: [0, 0],
  })
}

interface ClinicGroup {
  clinic_id: string
  clinic_name: string
  lat: number
  lng: number
  source: string | null
  items: SearchResult[]
}

function groupByClinics(results: SearchResult[]): ClinicGroup[] {
  const map = new Map<string, ClinicGroup>()
  for (const r of results) {
    if (r.lat == null || r.lng == null) continue
    if (!map.has(r.clinic_id)) {
      map.set(r.clinic_id, {
        clinic_id: r.clinic_id,
        clinic_name: r.clinic_name,
        lat: r.lat,
        lng: r.lng,
        source: r.source,
        items: [],
      })
    }
    map.get(r.clinic_id)!.items.push(r)
  }
  return Array.from(map.values())
}

// Recenter map whenever the results change
function MapBounds({ groups }: { groups: ClinicGroup[] }) {
  const map = useMap()
  useEffect(() => {
    if (groups.length === 0) return
    const bounds = L.latLngBounds(groups.map((g) => [g.lat, g.lng]))
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 })
  }, [groups, map])
  return null
}

interface MapViewProps {
  results: SearchResult[]
}

export function MapView({ results }: MapViewProps) {
  const groups = groupByClinics(results)

  // Default center: Алматы
  const defaultCenter: [number, number] = [43.2381, 76.8819]

  if (groups.length === 0) {
    return (
      <div className="flex h-[520px] items-center justify-center rounded-xl border bg-muted text-sm text-muted-foreground">
        Для отображения карты нет клиник с координатами
      </div>
    )
  }

  return (
    <div className="h-[520px] w-full overflow-hidden rounded-xl border">
      <MapContainer
        center={defaultCenter}
        zoom={11}
        className="h-full w-full"
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapBounds groups={groups} />
        {groups.map((g) => (
          <Marker
            key={g.clinic_id}
            position={[g.lat, g.lng]}
            icon={makeIcon(g.source)}
          >
            <Popup minWidth={200}>
              <div className="text-sm">
                <p className="font-semibold leading-snug">{g.clinic_name}</p>
                <ul className="mt-1.5 space-y-0.5">
                  {g.items.map((item, i) => (
                    <li key={i} className="flex justify-between gap-4 text-xs">
                      <span className="text-muted-foreground">{item.service_name}</span>
                      <span className="font-medium text-foreground whitespace-nowrap">
                        {formatPrice(item.price_kzt)}
                      </span>
                    </li>
                  ))}
                </ul>
                {g.items[0]?.source_url && (
                  <a
                    href={g.items[0].source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 block text-xs text-primary hover:underline"
                  >
                    На сайт →
                  </a>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}
