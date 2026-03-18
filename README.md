# Публичный пакет учебных кейсов: Excel, BI и Python

Этот подпроект подготовлен как публичный набор образовательных артефактов для занятия по аналитике данных. Внутри лежат датасеты, Excel-книга, Jupyter notebook, конфигурация BI-стенда, готовые иллюстрации и инструкции по запуску.

## Что входит

- `excel_legal_ai` - кейс про пилот ИИ для юристов в банке: импорт CSV, очистка, сводная таблица, итоговая визуализация и workbook в Excel.
- `bi_metabase_contact_center` - кейс для open-source BI на базе `Metabase` и `PostgreSQL`: локальный дашборд по обучению контакт-центра на основе речевой аналитики.
- `python_client_clusters` - кейс по кластеризации клиентов банка: датасет, пошаговая тетрадь и готовый HTML-отчет.
- `bank_products_basic_methods` - кейс по базовым методам анализа: первичный осмотр, пропуски и выбросы, сводные таблицы, линейная регрессия, интерпретация и управленческие выводы.

## Что уже можно публиковать

В репозиторий специально включены:

- CSV-датасеты;
- Excel workbook `.xlsx`;
- Jupyter notebook `.ipynb`;
- `docker-compose.yml` и скрипты запуска BI-кейса;
- PNG и SVG-иллюстрации для слайдов;
- README по каждому кейсу.

## Быстрый старт по разделам

## Как открыть подпроект в IDE отдельно от родительского репозитория

В папке уже создан отдельный `.git`, поэтому IDE должна видеть этот каталог как самостоятельный репозиторий. Для VS Code / Cursor можно открыть либо саму папку `public_analytics_training_cases`, либо workspace-файл `public_analytics_training_cases.code-workspace`.

### Excel

Откройте [excel_legal_ai/README.md](excel_legal_ai/README.md). Там лежат:

- сырой CSV для импорта;
- очищенный CSV для сравнения;
- готовая учебная книга `legal_ai_contract_review_training.xlsx`.

### BI

Откройте [bi_metabase_contact_center/README.md](bi_metabase_contact_center/README.md). Для запуска нужен Docker. После `./run_metabase_case.sh` поднимется `Metabase`, и вы сможете показать как готовый дашборд, так и ручную сборку виджета.

### Python: кластеризация клиентов

Откройте [python_client_clusters/README.md](python_client_clusters/README.md). Для пошагового показа лучше использовать `VS Code` с расширениями `Python` и `Jupyter`, либо `Jupyter Lab`.

### Python: базовые методы анализа

Откройте [bank_products_basic_methods/README.md](bank_products_basic_methods/README.md). Внутри лежат:

- синтетический набор данных по банковским продуктам;
- тетрадь с пошаговым сценарием анализа;
- готовые PNG-графики и таблицы для слайдов;
- скрипт `build_case.py` для пересборки кейса.

## Установка зависимостей для Python-кейса

Если хотите запускать notebook локально, создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Публикация

Пошаговая инструкция по публикации этого подпроекта в отдельный публичный репозиторий лежит в [PUBLISHING.md](PUBLISHING.md).
