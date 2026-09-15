# NVR K8204-W — реверс протокола bubble

## Параметры
- IP: 192.168.2.177
- Логин: admin
- Пароль: pass

## Протокол
GET /bubble/live?ch=N&stream=S
→ HTTP + XML + #### + H.264

## Инициализация
1. GET
2. PKT1 (58 байт) — admin
3. PKT2 (18 байт)
4. PKT3 (26 байт) — per channel

ВАЖНО: TCP_NODELAY + пауза 1 сек между пакетами.

## CGI API
Чтение:  <envload type="0"><encodesub chn="N"/>
Запись:  <envload type="1"><encodesub chn="N" fmt="5" .../>
Копия:   <copyg chn="0" type="6" channels="14"/>

## Запуск
~/start_nvr.sh

## Стоп
~/stop_nvr.sh
