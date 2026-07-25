(() => {
    "use strict";

    const NOTIFICATION_DURATION = 5000;
    const RECONNECT_DELAY = 3000;

    let reconnectTimer = null;
    let socket = null;

    function getWebSocketUrl() {
        const protocol = window.location.protocol === "https:"
            ? "wss:"
            : "ws:";

        return `${protocol}//${window.location.host}/ws/notifications/`;
    }

    function createNotificationContainer() {
        let container = document.getElementById(
            "notifications-container"
        );

        if (container) {
            return container;
        }

        container = document.createElement("div");
        container.id = "notifications-container";

        container.setAttribute(
            "aria-live",
            "polite"
        );

        container.setAttribute(
            "aria-atomic",
            "false"
        );

        document.body.appendChild(container);

        return container;
    }

    function showNotification(message) {
        const container = createNotificationContainer();

        const notification = document.createElement("div");

        notification.className = "admin-notification";
        notification.setAttribute("role", "status");

        notification.textContent = message;

        container.appendChild(notification);

        window.setTimeout(() => {
            notification.classList.add(
                "admin-notification--hidden"
            );

            notification.addEventListener(
                "transitionend",
                () => notification.remove(),
                { once: true }
            );
        }, NOTIFICATION_DURATION);
    }

    function handleMessage(event) {
        let data;

        try {
            data = JSON.parse(event.data);
        } catch (error) {
            console.error(
                "Failed to parse WebSocket message:",
                error
            );

            return;
        }

        if (
            !data ||
            typeof data !== "object" ||
            typeof data.message !== "string"
        ) {
            return;
        }

        showNotification(data.message);
    }

    function scheduleReconnect() {
        if (reconnectTimer !== null) {
            return;
        }

        reconnectTimer = window.setTimeout(() => {
            reconnectTimer = null;
            connect();
        }, RECONNECT_DELAY);
    }

    function connect() {
        if (
            socket &&
            (
                socket.readyState === WebSocket.OPEN ||
                socket.readyState === WebSocket.CONNECTING
            )
        ) {
            return;
        }

        socket = new WebSocket(
            getWebSocketUrl()
        );

        socket.addEventListener(
            "open",
            () => {
                console.debug(
                    "Notification WebSocket connected."
                );
            }
        );

        socket.addEventListener(
            "message",
            handleMessage
        );

        socket.addEventListener(
            "error",
            (error) => {
                console.error(
                    "Notification WebSocket error:",
                    error
                );
            }
        );

        socket.addEventListener(
            "close",
            () => {
                console.debug(
                    "Notification WebSocket closed."
                );

                socket = null;
                scheduleReconnect();
            }
        );
    }

    function addStyles() {
        if (
            document.getElementById(
                "admin-notifications-styles"
            )
        ) {
            return;
        }

        const style = document.createElement("style");

        style.id = "admin-notifications-styles";

        style.textContent = `
            #notifications-container {
                position: fixed;
                top: 60px;
                right: 20px;
                z-index: 9999;

                display: flex;
                flex-direction: column;
                gap: 10px;

                width: min(420px, calc(100vw - 40px));

                pointer-events: none;
            }

            .admin-notification {
                box-sizing: border-box;

                width: 100%;
                padding: 14px 18px;

                border-radius: 6px;

                background: #417690;
                color: #ffffff;

                box-shadow:
                    0 4px 12px rgba(0, 0, 0, 0.2);

                font-size: 14px;
                line-height: 1.4;

                opacity: 1;
                transform: translateX(0);

                transition:
                    opacity 250ms ease,
                    transform 250ms ease;
            }

            .admin-notification--hidden {
                opacity: 0;
                transform: translateX(20px);
            }
        `;

        document.head.appendChild(style);
    }

    function initialize() {
        addStyles();
        connect();
    }

    if (
        document.readyState === "loading"
    ) {
        document.addEventListener(
            "DOMContentLoaded",
            initialize,
            { once: true }
        );
    } else {
        initialize();
    }
})();
