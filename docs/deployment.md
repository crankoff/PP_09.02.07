# Развёртывание FlowBoard

## Render Blueprint

1. Откройте [Deploy to Render](https://render.com/deploy?repo=https://github.com/crankoff/PP_09.02.07).
2. Войдите в Render и разрешите доступ к репозиторию.
3. Проверьте создание Free web service из `render.yaml`.
4. Дождитесь, когда `/api/health` вернёт `{"status":"ok","database":"ok"}`.
5. Откройте выданный URL в инкогнито и пройдите демо-сценарий.

Blueprint создаёт `SECRET_KEY` автоматически, включает Secure cookie и настраивает health check. На Free-плане SQLite хранится в `/tmp`: этого достаточно для проверочного демо, но данные могут сбрасываться при новом deploy или перезапуске. Для постоянного хранения нужно выбрать платный compute plan, добавить persistent disk с mount path `/var/data` и задать `DATABASE_PATH=/var/data/flowboard.db`.

## Docker

```bash
docker build -t flowboard .
docker volume create flowboard-data
docker run -d --name flowboard \
  -p 8000:8000 \
  -e SECRET_KEY='a-long-random-production-secret' \
  -v flowboard-data:/app/data \
  --restart unless-stopped \
  flowboard
```

## Проверка после деплоя

- Главная страница открывается в инкогнито без ошибок 4xx/5xx.
- Вход `demo@example.com` / `Demo123!` работает.
- Новая задача появляется и переходит между колонками.
- На платной конфигурации с persistent disk: после перезапуска сервиса задача остаётся.
- `/api/health` отвечает `200` и `database=ok`.
- В консоли браузера нет CSP, JavaScript и network-ошибок.

## Резервные копии

Для экземпля Docker резервную копию можно создать без остановки:

```bash
docker exec flowboard python scripts/db_admin.py backup /app/data/flowboard-backup.db
```

Копию следует выгрузить во внешнее хранилище и периодически проверять тестовым восстановлением.
