# WebSocket-API erweitern und im Frontend nutzen

Diese Übersicht ist für den typischen Fall gedacht: Du willst auf dem Server einen neuen WebSocket-Kanal oder neue WebSocket-Nachrichten ergänzen und diese anschließend im Frontend konsumieren.

Das wichtigste Vorbild im Projekt ist der AI-Chat:

- Server-Route: [src/openbook/asgi.py](./src/openbook/asgi.py)
- Python-Nachrichtenvertrag: [src/openbook/ai/messages/chat.py](./src/openbook/ai/messages/chat.py)
- Server-Consumer: [src/openbook/ai/consumers/chat.py](./src/openbook/ai/consumers/chat.py)
- Frontend-WebSocket-Client: [src/frontend/app/src/api/websocket.ts](./src/frontend/app/src/api/websocket.ts)
- Frontend-Store: [src/frontend/app/src/stores/ai-chat.ts](./src/frontend/app/src/stores/ai-chat.ts)

Im Alltag startest du einfach `npm start`. Damit laufen Django und das Frontend. Wenn du ein WebSocket-Feature erweiterst, testest du es normalerweise direkt gegen den laufenden Dev-Server.

## 1. Das mentale Modell

Ein WebSocket-Feature besteht in OpenBook meistens aus fünf Bausteinen:

1. einer URL-Route im ASGI-Router,
2. Python-Nachrichtenklassen für eingehende und ausgehende Messages,
3. einem Consumer mit `handle_*`-Methoden,
4. einem Frontend-Store oder einer ähnlichen Logikschicht,
5. TypeScript-Typen für genau dieselben Nachrichten.

Der entscheidende Unterschied zur REST-API: Die TypeScript-Typen werden hier derzeit nicht automatisch aus der Server-Spezifikation generiert. In [src/frontend/app/src/stores/ai-chat.ts](./src/frontend/app/src/stores/ai-chat.ts) ist das ausdrücklich dokumentiert.

Praktisch bedeutet das: Wenn du auf der Python-Seite eine WebSocket-Message änderst, musst du die passenden TypeScript-Typen im Frontend von Hand mitziehen.

## 2. Der normale Ablauf für ein neues WebSocket-Feature

Wenn du ein neues WebSocket-Feature einführen willst, ist die Reihenfolge meistens so:

1. Python-Nachrichten definieren.
2. Consumer-Handler implementieren.
3. Route im ASGI-Router registrieren.
4. Frontend-Typen spiegeln.
5. Einen Store oder eine vergleichbare Client-Logik bauen.
6. Erst danach die eigentliche UI-Komponente anschließen.

Diese Reihenfolge ist wichtig, weil der Nachrichtenvertrag zuerst stehen sollte. Die UI ist der letzte Schritt, nicht der erste.

## 3. Schritt 1: Python-Nachrichten definieren

Der Nachrichtenvertrag lebt im AI-Chat-Beispiel in [src/openbook/ai/messages/chat.py](./src/openbook/ai/messages/chat.py).

Dort gibt es zwei Arten von Typen:

- Payload-Modelle, also die Struktur der eigentlichen Daten
- Message-Klassen mit `action` und `payload`

Ein kleines Beispiel aus dem Muster:

```python
class ChatInputPayload(BaseModel):
    format: ChatMessageFormat
    content: str

class ChatInput(BaseMessage):
    action: Literal["chat_input"] = "chat_input"
    payload: ChatInputPayload
```

Das ist das Grundprinzip: Jede Nachricht hat ein eindeutiges `action`-Feld. Darüber werden eingehende und ausgehende Nachrichten später im Consumer und im Frontend geroutet.

Wenn du zum Beispiel ein neues Feature `notifications` bauen willst, könnte das so aussehen:

```python
from chanx.messages.base import BaseMessage
from pydantic import BaseModel
from typing import Literal

class SubscribeNotificationsPayload(BaseModel):
    user_id: int

class SubscribeNotifications(BaseMessage):
    action: Literal["subscribe_notifications"] = "subscribe_notifications"
    payload: SubscribeNotificationsPayload

class NotificationPayload(BaseModel):
    title: str
    content: str

class NotificationMessage(BaseMessage):
    action: Literal["notification"] = "notification"
    payload: NotificationPayload
```

Faustregel: Zuerst sauber benannte Nachrichten und Payloads entwerfen, erst danach die eigentliche Handler-Logik schreiben.

## 4. Schritt 2: Consumer-Handler implementieren

Der Consumer im AI-Chat liegt in [src/openbook/ai/consumers/chat.py](./src/openbook/ai/consumers/chat.py).

Wichtig sind dort drei Dinge:

1. Der Consumer ist mit `@channel(...)` beschrieben.
2. Jede eingehende Nachricht bekommt eine `handle_*`-Methode mit `@ws_handler(...)`.
3. Der Rückgabewert einer Handler-Methode ist wieder eine typisierte Message.

Ein Beispiel aus dem bestehenden Code:

```python
@ws_handler(
    summary     = "Get Chat History",
    description = "Retrieve the full chat history from the server",
)
async def handle_get_chat_history(self, message: GetChatHistory) -> ChatHistory:
    return ChatHistory(payload=ChatHistoryPayload(messages=self.chat_history))
```

Und ein zweites wichtiges Muster aus demselben Consumer:

```python
await self.send_message(user_message)
return response_message
```

Das zeigt zwei Kommunikationsarten:

- `await self.send_message(...)` für zusätzliche Nachrichten während einer laufenden Verarbeitung
- `return ...` für die abschließende Antwort der Handler-Methode

Für ein neues Feature könnte ein einfacher Consumer-Handler so aussehen:

```python
@ws_handler(
    summary     = "Subscribe to notifications",
    description = "Register the current client for notification updates",
)
async def handle_subscribe_notifications(
    self,
    message: SubscribeNotifications,
) -> NotificationMessage:
    return NotificationMessage(
        payload=NotificationPayload(
            title="Verbindung steht",
            content=f"Abo für User {message.payload.user_id} aktiv",
        ),
    )
```

Faustregel: Halte die Handler-Signatur immer eng an deinen Nachrichtentyp gebunden. Dann bleibt das Feature nachvollziehbar und die AsyncAPI-Dokumentation bleibt brauchbar.

## 5. Schritt 3: Route im ASGI-Router registrieren

Die WebSocket-Routen werden in OpenBook zentral in [src/openbook/asgi.py](./src/openbook/asgi.py) registriert.

Das bestehende Beispiel sieht so aus:

```python
URLRouter([
    path("ws/ai/chat", ChatConsumer.as_asgi())
])
```

Wenn du einen neuen Consumer anlegst, ergänzt du dort den Pfad. Zum Beispiel:

```python
URLRouter([
    path("ws/ai/chat", ChatConsumer.as_asgi()),
    path("ws/notifications", NotificationsConsumer.as_asgi()),
])
```

Wichtig: In diesem Projekt werden die WebSocket-Routen bewusst zentral in [src/openbook/asgi.py](./src/openbook/asgi.py) gepflegt, nicht verteilt in den einzelnen Django-Apps.

## 6. Schritt 4: AsyncAPI-Ausgabe prüfen

Über die Chanx-Integration wird aus `@channel(...)` und `@ws_handler(...)` eine AsyncAPI-Beschreibung erzeugt. Die Django-URL-Konfiguration bindet dafür unter [src/openbook/urls.py](./src/openbook/urls.py) `chanx.channels.urls` unter `ws/` ein.

Für die Praxis heißt das: Nachdem du Consumer und Nachrichten angepasst hast, solltest du kurz prüfen, ob die WebSocket-Dokumentation sauber erzeugt wird. Im laufenden Dev-System ist die Doku typischerweise unter `/ws/docs/` erreichbar.

Das ersetzt im Moment aber noch nicht die TypeScript-Typen im Frontend. Diese musst du weiterhin manuell pflegen.

## 7. Schritt 5: TypeScript-Nachrichten spiegeln

Das ist der wichtigste Stolperstein für Anfänger: Anders als bei REST gibt es aktuell keine automatische Generierung der Frontend-Typen aus der AsyncAPI-Spezifikation.

Im AI-Chat sind die passenden TypeScript-Typen deshalb direkt in [src/frontend/app/src/stores/ai-chat.ts](./src/frontend/app/src/stores/ai-chat.ts) definiert.

Das Python-Beispiel

```python
class ChatInput(BaseMessage):
    action: Literal["chat_input"] = "chat_input"
    payload: ChatInputPayload
```

wird dort manuell gespiegelt als

```ts
export type ChatInput = {
    action: "chat_input";
    payload: ChatInputPayload;
};
```

Für ein neues Feature musst du dasselbe tun. Beispiel:

```ts
export type SubscribeNotificationsPayload = {
    user_id: number;
};

export type SubscribeNotifications = {
    action: "subscribe_notifications";
    payload: SubscribeNotificationsPayload;
};

export type NotificationPayload = {
    title: string;
    content: string;
};

export type NotificationMessage = {
    action: "notification";
    payload: NotificationPayload;
};
```

Danach fasst du die Typen normalerweise zu zwei Unions zusammen:

```ts
export type SentMessages = SubscribeNotifications;
export type ReceivedMessages = NotificationMessage;
```

Faustregel: Wenn du auf der Python-Seite `action`, `payload` oder Feldnamen änderst, musst du die TypeScript-Seite sofort synchron nachziehen.

## 8. Schritt 6: Frontend-Store bauen

Im Projekt landet die eigentliche WebSocket-Kommunikation typischerweise nicht direkt in der Svelte-Komponente, sondern in einem Store. Das AI-Chat-Beispiel in [src/frontend/app/src/stores/ai-chat.ts](./src/frontend/app/src/stores/ai-chat.ts) zeigt dieses Muster sehr gut.

Der Ablauf dort ist:

1. Der Store holt sich einen WebSocket-Client über `api.ws(...)`.
2. Er registriert Status-Listener.
3. Er registriert Message-Handler je `action`.
4. Er stellt kleine Methoden bereit, die fachlich sinnvoll benannt sind.

Das Grundmuster sieht so aus:

```ts
if (!this.#ws) this.#ws = await api.ws("/ai/chat");

this.#ws.setMessageHandler("chat_history", (message: ChatHistory) => {
    // Zustand aktualisieren
});

await this.#ws.connect();
```

Für ein neues Feature könnte ein Store so aussehen:

```ts
import type { WebSocketClient } from "../api/websocket.js";
import { ReadableStore } from "../utils/store.js";
import api from "../api/index.js";

type NotificationState = {
    connected: boolean;
    messages: NotificationPayload[];
};

export class NotificationStore extends ReadableStore<NotificationState> {
    #ws?: WebSocketClient<SubscribeNotifications, NotificationMessage>;

    constructor() {
        super({ connected: false, messages: [] });
    }

    async connect() {
        if (!this.#ws) this.#ws = await api.ws("/notifications");

        this.#ws.setConnectionStatusListener(async status => {
            this.update(state => ({
                ...state,
                connected: status === "connected",
            }));
        });

        this.#ws.setMessageHandler("notification", message => {
            this.update(state => ({
                ...state,
                messages: [...state.messages, message.payload],
            }));
        });

        await this.#ws.connect();
    }

    async subscribe(userId: number) {
        await this.#ws?.send({
            action: "subscribe_notifications",
            payload: { user_id: userId },
        });
    }
}
```

Der Vorteil dieses Musters: Die UI muss das Protokoll nicht im Detail kennen. Sie benutzt nur noch Store-Methoden.

## 9. Schritt 7: UI-Komponente anschließen

Erst jetzt kommt die Svelte-Komponente dran. Im AI-Chat sieht man in [src/frontend/app/src/components/ai-chat/AiChatPane.svelte](./src/frontend/app/src/components/ai-chat/AiChatPane.svelte), wie schlank die UI dadurch bleibt:

```ts
const aiChat = new AiChatStore();

onMount(() => {
    void aiChat.connect();

    return () => {
        void aiChat.disconnect();
    };
});
```

Für ein eigenes Feature sollte die Komponente idealerweise nur noch:

- den Store erzeugen,
- beim Mount verbinden,
- beim Unmount trennen,
- den Store-Zustand rendern,
- und auf Benutzeraktionen mit Store-Methoden reagieren.

Faustregel: Wenn in deiner Svelte-Komponente viele `setMessageHandler(...)`-Aufrufe oder rohe `action`-Strings auftauchen, ist die Logik wahrscheinlich in der falschen Schicht gelandet.

## 10. Welche Datei du wofür anfasst

Wenn du die WebSocket-API erweiterst, landest du typischerweise in genau diesen Dateien:

1. Neue oder geänderte Python-Nachrichten: [src/openbook/ai/messages/chat.py](./src/openbook/ai/messages/chat.py) oder ein entsprechendes neues Message-Modul
2. Neue oder geänderte Consumer-Logik: [src/openbook/ai/consumers/chat.py](./src/openbook/ai/consumers/chat.py) oder ein neuer Consumer
3. Neue Route: [src/openbook/asgi.py](./src/openbook/asgi.py)
4. Frontend-Typen und Client-Logik: meist ein neuer Store nach dem Vorbild von [src/frontend/app/src/stores/ai-chat.ts](./src/frontend/app/src/stores/ai-chat.ts)
5. UI-Anschluss: eine Svelte-Komponente nach dem Vorbild von [src/frontend/app/src/components/ai-chat/AiChatPane.svelte](./src/frontend/app/src/components/ai-chat/AiChatPane.svelte)

## 11. Die wichtigsten Beispiele im Projekt

- Zentrale WebSocket-Routen: [src/openbook/asgi.py](./src/openbook/asgi.py)
- Python-Nachrichtenvertrag: [src/openbook/ai/messages/chat.py](./src/openbook/ai/messages/chat.py)
- Consumer mit `@channel` und `@ws_handler`: [src/openbook/ai/consumers/chat.py](./src/openbook/ai/consumers/chat.py)
- Browser-WebSocket-Wrapper mit Reconnect und Message-Routing: [src/frontend/app/src/api/websocket.ts](./src/frontend/app/src/api/websocket.ts)
- Frontend-Store mit manuell gespiegelten Nachrichtentypen: [src/frontend/app/src/stores/ai-chat.ts](./src/frontend/app/src/stores/ai-chat.ts)
- UI, die nur noch den Store benutzt: [src/frontend/app/src/components/ai-chat/AiChatPane.svelte](./src/frontend/app/src/components/ai-chat/AiChatPane.svelte)
