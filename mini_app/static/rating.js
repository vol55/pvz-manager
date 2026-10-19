document.addEventListener("DOMContentLoaded", async () => {
    const tg = window.Telegram?.WebApp;
    tg?.ready();
    tg?.expand();

    const loading = document.getElementById("loading");
    const app = document.getElementById("app");
    const periodSwitcher = document.getElementById("period-switcher");
    const periodInfo = document.getElementById("period-info");
    const sections = document.getElementById("sections");
    const errorMessage = document.getElementById("error-message");

    const prefix = new URL(".", location.href).pathname.replace(/\/$/, "");

    const state = {
        userId: null,
        periods: {
            current: null,
            previous: null,
        },
        activePeriod: "current",
    };

    const METRICS = [
        {label: "Приемка", sum: "acceptance_sum", place: "acceptance_place"},
        {label: "Зависшие", sum: "stuck_sum", place: "stuck_place"},
        {label: "Подмена", sum: "replacement_sum", place: "replacement_place"},
        {label: "Брак", sum: "defect_sum", place: "defect_place"},
        {label: "Опоздания", sum: "late_sum", place: "late_place"},
        {label: "Рейтинг", sum: "rating_sum", place: "rating_place"},
    ];

    let cardIdSequence = 0;

    function showApp() {
        loading.hidden = true;
        app.hidden = false;
    }

    function showError(message) {
        sections.innerHTML = "";
        periodSwitcher.hidden = true;
        periodInfo.hidden = true;
        errorMessage.hidden = false;
        errorMessage.textContent = message;
        showApp();
    }

    function toNumberOrNull(value) {
        if (value === null || value === undefined || value === "") {
            return null;
        }

        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function normalizePeriod(period) {
        if (!period || typeof period !== "object") {
            return null;
        }

        return {
            title: period.title || "Период",
            date_range: period.date_range || "",
            places: toNumberOrNull(period.places),
            employees: Array.isArray(period.employees) ? period.employees : [],
        };
    }

    function sortEmployees(list) {
        return [...list].sort((a, b) => {
            const aPlace = Number(a?.place ?? 999999);
            const bPlace = Number(b?.place ?? 999999);
            return aPlace - bPlace;
        });
    }

    function isSameId(a, b) {
        if (a === null || a === undefined || b === null || b === undefined) {
            return false;
        }

        return String(a) === String(b);
    }

    function hasPlace(value) {
        return value !== null && value !== undefined && value !== "";
    }

    function formatValue(value) {
        return value === null || value === undefined || value === "" ? "—" : String(value);
    }

    function filterEmployeesByPeriodPlaces(employees, maxPlace) {
        return employees.filter((item) => {
            if (!hasPlace(item.place)) {
                return false;
            }

            const place = Number(item.place);

            if (!Number.isFinite(place)) {
                return false;
            }

            if (maxPlace === null) {
                return true;
            }

            return place <= maxPlace;
        });
    }

    function createMetricRow(label, sum, place) {
        const row = document.createElement("div");
        row.className = "metric-row";

        const labelEl = document.createElement("div");
        labelEl.className = "metric-label";
        labelEl.textContent = label;

        const valueWrap = document.createElement("div");
        valueWrap.className = "metric-value-wrap";

        const sumEl = document.createElement("div");
        sumEl.className = "metric-value";
        sumEl.textContent = formatValue(sum);

        const placeEl = document.createElement("div");
        placeEl.className = "metric-place";
        placeEl.textContent = `Место: ${formatValue(place)}`;

        valueWrap.appendChild(sumEl);
        valueWrap.appendChild(placeEl);

        row.appendChild(labelEl);
        row.appendChild(valueWrap);

        return row;
    }

    function openEmployeeCard(card) {
        if (card.classList.contains("open")) {
            return;
        }

        const toggle = card.querySelector(".employee-toggle");
        const collapse = card.querySelector(".employee-collapse");

        card.classList.add("open");
        toggle.setAttribute("aria-expanded", "true");
        collapse.setAttribute("aria-hidden", "false");

        collapse.style.height = "0px";
        collapse.style.opacity = "0";

        const targetHeight = collapse.scrollHeight;

        requestAnimationFrame(() => {
            collapse.style.height = `${targetHeight}px`;
            collapse.style.opacity = "1";
        });

        const handleEnd = (event) => {
            if (event.propertyName !== "height") {
                return;
            }

            collapse.style.height = "auto";
            collapse.removeEventListener("transitionend", handleEnd);
        };

        collapse.addEventListener("transitionend", handleEnd);
    }

    function closeEmployeeCard(card) {
        if (!card.classList.contains("open")) {
            return;
        }

        const toggle = card.querySelector(".employee-toggle");
        const collapse = card.querySelector(".employee-collapse");

        const currentHeight = collapse.scrollHeight;
        collapse.style.height = `${currentHeight}px`;
        collapse.style.opacity = "1";

        collapse.offsetHeight;

        card.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        collapse.setAttribute("aria-hidden", "true");

        requestAnimationFrame(() => {
            collapse.style.height = "0px";
            collapse.style.opacity = "0";
        });
    }

    function toggleEmployeeCard(card) {
        if (card.classList.contains("open")) {
            closeEmployeeCard(card);
        } else {
            openEmployeeCard(card);
        }
    }

    function createEmployeeCard(employee) {
        const card = document.createElement("article");
        card.className = "employee-card";

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "employee-toggle";

        const summaryLeft = document.createElement("div");
        summaryLeft.className = "employee-summary-left";

        const name = document.createElement("div");
        name.className = "employee-name";
        name.textContent = employee.employee || "Без имени";

        const subtitle = document.createElement("div");
        subtitle.className = "employee-subtitle";
        subtitle.textContent = employee.main_pvz || "ПВЗ не указан";

        summaryLeft.appendChild(name);
        summaryLeft.appendChild(subtitle);

        const summaryRight = document.createElement("div");
        summaryRight.className = "employee-summary-right";

        const placeBadge = document.createElement("div");
        placeBadge.className = "place-badge";
        placeBadge.textContent = `#${formatValue(employee.place)}`;

        const chevron = document.createElement("span");
        chevron.className = "employee-chevron";
        chevron.setAttribute("aria-hidden", "true");
        chevron.innerHTML = `
            <svg viewBox="0 0 20 20" fill="none">
                <path d="M5 8l5 5 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path>
            </svg>
        `;

        summaryRight.appendChild(placeBadge);
        summaryRight.appendChild(chevron);

        toggle.appendChild(summaryLeft);
        toggle.appendChild(summaryRight);

        const collapse = document.createElement("div");
        collapse.className = "employee-collapse";
        collapse.style.height = "0px";
        collapse.style.opacity = "0";
        collapse.setAttribute("aria-hidden", "true");

        const collapseId = `employee-collapse-${++cardIdSequence}`;
        collapse.id = collapseId;

        toggle.setAttribute("aria-controls", collapseId);
        toggle.setAttribute("aria-expanded", "false");

        const collapseInner = document.createElement("div");
        collapseInner.className = "employee-collapse-inner";

        const metrics = document.createElement("div");
        metrics.className = "employee-metrics";

        METRICS.forEach((metric) => {
            metrics.appendChild(
                createMetricRow(
                    metric.label,
                    employee[metric.sum],
                    employee[metric.place]
                )
            );
        });

        collapseInner.appendChild(metrics);
        collapse.appendChild(collapseInner);

        toggle.addEventListener("click", () => {
            toggleEmployeeCard(card);
        });

        card.appendChild(toggle);
        card.appendChild(collapse);

        return card;
    }

    function createSection(title, employees) {
        const section = document.createElement("section");
        section.className = "section-card";

        if (title) {
            const header = document.createElement("div");
            header.className = "section-header";

            const titleEl = document.createElement("h2");
            titleEl.className = "section-title";
            titleEl.textContent = title;

            header.appendChild(titleEl);
            section.appendChild(header);
        }

        const list = document.createElement("div");
        list.className = "employee-list";

        employees.forEach((employee) => {
            list.appendChild(createEmployeeCard(employee));
        });

        section.appendChild(list);
        return section;
    }

    function renderPeriodSwitcher() {
        const availablePeriods = [
            {key: "current", label: "Этот период", data: state.periods.current},
            {key: "previous", label: "Прошлый", data: state.periods.previous},
        ].filter((item) => item.data);

        periodSwitcher.innerHTML = "";

        if (availablePeriods.length <= 1) {
            periodSwitcher.hidden = true;
            return;
        }

        availablePeriods.forEach((item) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = `period-button${state.activePeriod === item.key ? " active" : ""}`;
            button.textContent = item.label;
            button.setAttribute("aria-pressed", state.activePeriod === item.key ? "true" : "false");

            button.addEventListener("click", () => {
                if (state.activePeriod === item.key) {
                    return;
                }

                state.activePeriod = item.key;
                render();
            });

            periodSwitcher.appendChild(button);
        });

        periodSwitcher.hidden = false;
    }

    function renderPeriodInfo(period) {
        periodInfo.innerHTML = "";

        if (!period) {
            periodInfo.hidden = true;
            return;
        }

        const title = document.createElement("div");
        title.className = "period-title";
        title.textContent = period.title || "Период";

        const date = document.createElement("div");
        date.className = "period-date";
        date.textContent = period.date_range || "";

        periodInfo.appendChild(title);
        periodInfo.appendChild(date);
        periodInfo.hidden = false;
    }

    function renderSections(period) {
        sections.innerHTML = "";

        if (!period) {
            const empty = document.createElement("div");
            empty.className = "empty-state";
            empty.textContent = "Нет данных за выбранный период";
            sections.appendChild(empty);
            return;
        }

        const employees = sortEmployees(period.employees || []);
        const maxPlace = toNumberOrNull(period.places);

        // Ограничение по places применяется только для блока "Все сотрудники"
        const visibleEmployees = filterEmployeesByPeriodPlaces(employees, maxPlace);

        const userId = state.userId;

        // "Моя статистика" — самого себя показываем
        const employeeMatches = employees.filter((item) =>
            isSameId(item.employee_tg_id, userId)
        );

        // "Мои сотрудники" — ищем среди всех сотрудников,
        // но самого себя исключаем
        const responsibleMatches = employees.filter((item) =>
            isSameId(item.responsible_tg_id, userId) &&
            !isSameId(item.employee_tg_id, userId)
        );

        const seniorMatches = employees.filter((item) =>
            isSameId(item.senior_pvz_tg_id, userId) &&
            !isSameId(item.employee_tg_id, userId)
        );

        let hasContent = false;

        if (employeeMatches.length > 0) {
            sections.appendChild(createSection("Моя статистика", employeeMatches));
            hasContent = true;
        }

        if (seniorMatches.length > 0) {
            sections.appendChild(createSection("Мои сотрудники", seniorMatches));
            hasContent = true;
        } else if (responsibleMatches.length > 0) {
            sections.appendChild(createSection("Мои сотрудники", responsibleMatches));
            hasContent = true;
        }

        if (visibleEmployees.length > 0) {
            sections.appendChild(createSection("Все сотрудники", visibleEmployees));
            hasContent = true;
        }

        if (!hasContent) {
            const empty = document.createElement("div");
            empty.className = "empty-state";
            empty.textContent = "Список сотрудников пуст";
            sections.appendChild(empty);
        }
    }

    function render() {
        errorMessage.hidden = true;

        const period = state.periods[state.activePeriod];
        renderPeriodSwitcher();
        renderPeriodInfo(period);
        renderSections(period);
        showApp();
    }

    function setupBackHandling() {
        if (!tg) {
            return;
        }

        const closeApp = () => {
            try {
                tg.close();
            } catch (_) {
            }
        };

        if (tg.BackButton) {
            tg.BackButton.show();
            tg.BackButton.onClick(closeApp);
        }

        try {
            if (!history.state || !history.state.telegramMiniAppRoot) {
                history.pushState({telegramMiniAppRoot: true}, "");
            }

            window.addEventListener("popstate", () => {
                closeApp();
            });
        } catch (_) {
        }
    }

    async function validate() {
        const initData = tg?.initData || "";

        const response = await fetch(`${prefix}/api/rating`, {
            method: "POST",
            headers: {
                "X-Telegram-Init-Data": initData,
            },
        });

        let payload = {};
        try {
            payload = await response.json();
        } catch (_) {
            payload = {};
        }

        if (!response.ok) {
            throw new Error(payload.detail || "Ошибка авторизации");
        }

        return payload;
    }

    try {
        setupBackHandling();

        const data = await validate();
        const statistics = data?.statistics || data?.employees || {};

        state.userId = data?.id ?? null;
        state.periods.current = normalizePeriod(statistics?.current);
        state.periods.previous = normalizePeriod(statistics?.previous);

        if (state.periods.current) {
            state.activePeriod = "current";
        } else if (state.periods.previous) {
            state.activePeriod = "previous";
        }

        render();
    } catch (error) {
        showError(
            error instanceof Error ? error.message : "Ощибка сервера"
        );
    }
});
