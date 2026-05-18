# Dispute MCP Processing

Frontend для рабочего места операциониста находится в `frontend/`.

## Запуск UI

```bash
cd frontend
npm install
npm run dev
```

Приложение сделано без backend-интеграции: очередь диспутов, парсинг идентификаторов, ответы MCP-серверов и итоговый ответ моделируются на клиенте.
